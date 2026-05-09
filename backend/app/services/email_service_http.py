"""
HTTP-based Email Service using SendGrid and Mailgun APIs.

This service provides an alternative to SMTP for sending emails,
which works better on cloud platforms like Render.com.

Supports:
- SendGrid API
- Mailgun API
- Automatic fallback between providers
"""

import httpx
import logging
from typing import Optional, Dict, List
from jinja2 import Environment, FileSystemLoader
from app.config import Settings
from app.models.product import Product
from app.models.search_request import SearchRequest
import asyncio
from datetime import datetime

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class EmailServiceHTTP:
    """
    HTTP-based email service supporting SendGrid and Mailgun.
    
    Features:
    - Multiple provider support (SendGrid, Mailgun)
    - Automatic fallback between providers
    - Retry logic with exponential backoff
    - Template rendering with Jinja2
    """
    
    def __init__(self, config: Settings):
        """Initialize email service with configuration"""
        self.config = config
        self.template_env = Environment(
            loader=FileSystemLoader("app/templates")
        )
        
        # Determine which provider to use
        self.primary_provider = self._determine_primary_provider()
        self.fallback_provider = self._determine_fallback_provider()
        
        logger.info(f"Email service initialized with primary provider: {self.primary_provider}")
        if self.fallback_provider:
            logger.info(f"Fallback provider available: {self.fallback_provider}")
    
    def _determine_primary_provider(self) -> Optional[str]:
        """Determine which email provider to use as primary"""
        if self.config.SENDGRID_API_KEY:
            return "sendgrid"
        elif self.config.MAILGUN_API_KEY and self.config.MAILGUN_DOMAIN:
            return "mailgun"
        elif self.config.SMTP_USERNAME and self.config.SMTP_PASSWORD:
            logger.warning("Only SMTP credentials available. Consider using SendGrid or Mailgun for better reliability.")
            return None
        return None
    
    def _determine_fallback_provider(self) -> Optional[str]:
        """Determine fallback provider if primary fails"""
        if self.primary_provider == "sendgrid":
            if self.config.MAILGUN_API_KEY and self.config.MAILGUN_DOMAIN:
                return "mailgun"
        elif self.primary_provider == "mailgun":
            if self.config.SENDGRID_API_KEY:
                return "sendgrid"
        return None
    
    async def _send_via_sendgrid(
        self,
        to_email: str,
        subject: str,
        html_content: str
    ) -> bool:
        """
        Send email via SendGrid API.
        
        Args:
            to_email: Recipient email address
            subject: Email subject line
            html_content: HTML content of the email
            
        Returns:
            bool: True if successful, False otherwise
        """
        logger.info(f"EmailServiceHTTP: Attempting to send email to {to_email} via SendGrid")
        if not self.config.SENDGRID_API_KEY:
            logger.error("SendGrid API key not configured")
            return False
        
        url = "https://api.sendgrid.com/v3/mail/send"
        headers = {
            "Authorization": f"Bearer {self.config.SENDGRID_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "personalizations": [
                {
                    "to": [{"email": to_email}],
                    "subject": subject
                }
            ],
            "from": {
                "email": self.config.EMAIL_FROM,
                "name": self.config.EMAIL_FROM_NAME
            },
            "content": [
                {
                    "type": "text/html",
                    "value": html_content
                }
            ]
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload, headers=headers)
                
                if response.status_code == 202:
                    logger.info(f"Email sent successfully via SendGrid to {to_email}")
                    return True
                else:
                    logger.error(
                        f"SendGrid API error: {response.status_code} - {response.text}"
                    )
                    return False
                    
        except Exception as e:
            logger.error(f"Error sending email via SendGrid: {str(e)}", exc_info=True)
            return False
    
    async def _send_via_mailgun(
        self,
        to_email: str,
        subject: str,
        html_content: str
    ) -> bool:
        """
        Send email via Mailgun API.
        
        Args:
            to_email: Recipient email address
            subject: Email subject line
            html_content: HTML content of the email
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.config.MAILGUN_API_KEY or not self.config.MAILGUN_DOMAIN:
            logger.error("Mailgun API key or domain not configured")
            return False
        
        url = f"https://api.mailgun.net/v3/{self.config.MAILGUN_DOMAIN}/messages"
        
        auth = ("api", self.config.MAILGUN_API_KEY)
        
        data = {
            "from": f"{self.config.EMAIL_FROM_NAME} <{self.config.EMAIL_FROM}>",
            "to": to_email,
            "subject": subject,
            "html": html_content
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, auth=auth, data=data)
                
                if response.status_code == 200:
                    logger.info(f"Email sent successfully via Mailgun to {to_email}")
                    return True
                else:
                    logger.error(
                        f"Mailgun API error: {response.status_code} - {response.text}"
                    )
                    return False
                    
        except Exception as e:
            logger.error(f"Error sending email via Mailgun: {str(e)}", exc_info=True)
            return False
    
    async def send_email_with_retry(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        max_retries: Optional[int] = None,
        initial_delay: Optional[float] = None
    ):
        """
        Send email with exponential backoff retry logic.
        Tries primary provider first, then fallback if available.
        
        Args:
            to_email: Recipient email address
            subject: Email subject line
            html_content: HTML content of the email
            max_retries: Maximum number of retry attempts
            initial_delay: Initial delay between retries in seconds
            
        Raises:
            Exception: If email sending fails after all retries
        """
        # Use config values if not provided
        if max_retries is None:
            max_retries = self.config.EMAIL_MAX_RETRIES
        if initial_delay is None:
            initial_delay = self.config.EMAIL_RETRY_DELAY
        
        # Check if email notifications are enabled
        if not self.config.ENABLE_EMAIL_NOTIFICATIONS:
            logger.warning("Email notifications are disabled. Skipping email send.")
            return
        
        # Validate configuration
        if not self.primary_provider:
            logger.error("No email provider configured. Please set up SendGrid or Mailgun.")
            raise ValueError("No email provider configured")
        
        # Try primary provider with retries
        for attempt in range(max_retries):
            try:
                success = await self._send_email_internal(
                    to_email, subject, html_content, self.primary_provider
                )
                
                if success:
                    logger.info(
                        f"Email sent successfully to {to_email} via {self.primary_provider} "
                        f"on attempt {attempt + 1}"
                    )
                    return
                
                # If not successful and we have retries left, wait before retry
                if attempt < max_retries - 1:
                    delay = initial_delay * (2 ** attempt)  # Exponential backoff
                    logger.warning(
                        f"Failed to send email via {self.primary_provider} "
                        f"(attempt {attempt + 1}/{max_retries}). "
                        f"Retrying in {delay} seconds..."
                    )
                    await asyncio.sleep(delay)
                    
            except Exception as e:
                logger.error(
                    f"Error on attempt {attempt + 1} with {self.primary_provider}: {str(e)}"
                )
                if attempt < max_retries - 1:
                    delay = initial_delay * (2 ** attempt)
                    await asyncio.sleep(delay)
        
        # If primary provider failed, try fallback
        if self.fallback_provider:
            logger.warning(
                f"Primary provider {self.primary_provider} failed. "
                f"Trying fallback provider {self.fallback_provider}"
            )
            
            try:
                success = await self._send_email_internal(
                    to_email, subject, html_content, self.fallback_provider
                )
                
                if success:
                    logger.info(
                        f"Email sent successfully to {to_email} via fallback provider "
                        f"{self.fallback_provider}"
                    )
                    return
            except Exception as e:
                logger.error(f"Fallback provider also failed: {str(e)}")
        
        # If we get here, all attempts failed
        raise Exception(
            f"Failed to send email to {to_email} after {max_retries} attempts "
            f"with {self.primary_provider}" +
            (f" and fallback {self.fallback_provider}" if self.fallback_provider else "")
        )
    
    async def _send_email_internal(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        provider: str
    ) -> bool:
        """
        Internal method to send email via specified provider.
        
        Args:
            to_email: Recipient email address
            subject: Email subject line
            html_content: HTML content of the email
            provider: Provider to use ('sendgrid' or 'mailgun')
            
        Returns:
            bool: True if successful, False otherwise
        """
        logger.info(f"EmailServiceHTTP: Attempting to send email to {to_email} via {provider}")
        
        if provider == "sendgrid":
            return await self._send_via_sendgrid(to_email, subject, html_content)
        elif provider == "mailgun":
            return await self._send_via_mailgun(to_email, subject, html_content)
        else:
            logger.error(f"Unknown email provider: {provider}")
            return False
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str
    ):
        """
        Core method to send email with retry logic.
        
        Args:
            to_email: Recipient email address
            subject: Email subject line
            html_content: HTML content of the email
            
        Raises:
            Exception: If email sending fails after retries
        """
        await self.send_email_with_retry(to_email, subject, html_content)
    
    async def send_match_notification(
        self,
        email: str,
        product: Product,
        search_request: SearchRequest
    ):
        """
        Send notification when product matches search criteria.
        
        Args:
            email: Recipient email address
            product: Product object that matched
            search_request: SearchRequest object that was matched against
            
        Raises:
            Exception: If email sending fails
        """
        logger.info(f"Sending match notification to {email} for product: {product.title}")
        try:
            # Load and render template
            template = self.template_env.get_template("emails/match_notification.html")
            
            # Prepare template context
            created_at_str = "Recently"
            if product.created_at:
                try:
                    if isinstance(product.created_at, str):
                        created_at_str = product.created_at
                    elif hasattr(product.created_at, 'strftime'):
                        created_at_str = product.created_at.strftime("%B %d, %Y at %I:%M %p")
                    else:
                        created_at_str = str(product.created_at)
                except Exception as e:
                    logger.warning(f"Could not format product.created_at: {e}")
                    created_at_str = "Recently"
            
            context = {
                "search_query": search_request.product_name,
                "product": {
                    "title": product.title,
                    "price": f"{product.price:.2f}" if product.price else "N/A",
                    "platform": product.platform.capitalize(),
                    "match_score": f"{product.match_score:.1f}" if product.match_score else "N/A",
                    "url": product.url,
                    "created_at": created_at_str
                }
            }
            
            # Render HTML content
            html_content = template.render(**context)
            
            # Create subject line
            subject = f"New Match Found: {product.title[:50]}{'...' if len(product.title) > 50 else ''}"
            
            # Send email
            await self.send_email(
                to_email=email,
                subject=subject,
                html_content=html_content
            )
            
            logger.info(f"Match notification sent successfully to {email}")
            
        except Exception as e:
            logger.error(f"Failed to send match notification to {email}: {str(e)}", exc_info=True)
            raise Exception(f"Failed to send match notification: {str(e)}")
    
    async def send_daily_digest(
        self,
        email: str,
        matches: List[Dict]
    ):
        """
        Send daily summary of all matches.
        
        Args:
            email: Recipient email address
            matches: List of dictionaries containing product and search_request data
            
        Raises:
            Exception: If email sending fails
        """
        logger.info(f"Preparing daily digest email for {email}")
        try:
            # Load and render template
            template = self.template_env.get_template("emails/daily_digest.html")
            
            # Prepare matches data for template
            formatted_matches = []
            for match in matches:
                product = match.get('product')
                search_request = match.get('search_request')
                
                if product and search_request:
                    formatted_matches.append({
                        "search_query": search_request.product_name,
                        "product": {
                            "title": product.title,
                            "price": f"{product.price:.2f}" if product.price else "N/A",
                            "platform": product.platform.capitalize(),
                            "match_score": f"{product.match_score:.1f}" if product.match_score else "N/A",
                            "url": product.url
                        }
                    })
            
            # Prepare template context
            date_str = datetime.now().strftime('%B %d, %Y')
            context = {
                "date": date_str,
                "matches": formatted_matches
            }
            
            # Render HTML content
            html_content = template.render(**context)
            
            # Create subject line
            match_count = len(formatted_matches)
            if match_count > 0:
                subject = f"Daily Digest: {match_count} New Match{'es' if match_count != 1 else ''} Found"
            else:
                subject = "Daily Digest: No New Matches Today"
            
            # Send email
            await self.send_email(
                to_email=email,
                subject=subject,
                html_content=html_content
            )
            
            logger.info(f"Daily digest sent successfully to {email}")
            
        except Exception as e:
            logger.error(f"Failed to send daily digest to {email}: {str(e)}", exc_info=True)
            raise Exception(f"Failed to send daily digest: {str(e)}")
    
    async def send_search_started(
        self,
        email: str,
        search_request: SearchRequest
    ):
        """
        Send confirmation email when a new search is started.
        
        Args:
            email: Recipient email address
            search_request: SearchRequest object that was just created
            
        Raises:
            Exception: If email sending fails
        """
        logger.info(f"Sending search started email to {email}")
        try:
            # Load and render template
            template = self.template_env.get_template("emails/search_started.html")
            
            # Build platforms list
            platforms = []
            if search_request.search_craigslist:
                platforms.append("Craigslist")
            if search_request.search_ebay:
                platforms.append("eBay")
            if search_request.search_facebook:
                platforms.append("Facebook Marketplace")
            
            # Prepare template context
            created_at_str = "Just now"
            if search_request.created_at:
                try:
                    if isinstance(search_request.created_at, str):
                        created_at_str = search_request.created_at
                    elif hasattr(search_request.created_at, 'strftime'):
                        created_at_str = search_request.created_at.strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        created_at_str = str(search_request.created_at)
                except Exception as e:
                    logger.warning(f"Could not format created_at: {e}")
                    created_at_str = "Just now"
            
            context = {
                "search_request": {
                    "product_name": search_request.product_name,
                    "budget": f"{search_request.budget:.2f}" if search_request.budget else "Not specified",
                    "platforms": platforms if platforms else ["All platforms"],
                    "search_interval": search_request.search_interval if hasattr(search_request, 'search_interval') else 2,
                    "created_at": created_at_str
                }
            }
            
            # Render HTML content
            html_content = template.render(**context)
            
            # Create subject line
            subject = f"Search Started: {search_request.product_name}"
            
            # Send email
            await self.send_email(
                to_email=email,
                subject=subject,
                html_content=html_content
            )
            
            logger.info(f"Search started confirmation sent successfully to {email}")
            
        except Exception as e:
            logger.error(f"Failed to send search started confirmation to {email}: {str(e)}", exc_info=True)
            raise Exception(f"Failed to send search started confirmation: {str(e)}")

# Made with Bob
