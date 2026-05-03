from aiosmtplib import SMTP
from jinja2 import Environment, FileSystemLoader
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.models.product import Product
from app.models.search_request import SearchRequest
from app.models.notification import Notification
from app.models.email_preference import EmailPreference
from app.config import Settings
from typing import List, Dict
import logging
from datetime import datetime
from sqlalchemy.orm import Session
            

# Configure logger
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)



class EmailService:
    def __init__(self, config: Settings):
        """Initialize email service with configuration"""
        self.config = config
        self.template_env = Environment(
            loader=FileSystemLoader("app/templates")
        )
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str
    ):
        """
        Core method to send email via SMTP.
        
        Args:
            to_email: Recipient email address
            subject: Email subject line
            html_content: HTML content of the email
            
        Raises:
            Exception: If email sending fails
        """
        # Check if email notifications are enabled
        if not self.config.ENABLE_EMAIL_NOTIFICATIONS:
            logger.warning("Email notifications are disabled. Skipping email send.")
            return
        
        # Validate configuration
        if not self.config.SMTP_USERNAME or not self.config.SMTP_PASSWORD:
            logger.error("SMTP credentials not configured. Cannot send email.")
            raise ValueError("SMTP credentials not configured")
        
        if not self.config.EMAIL_FROM:
            logger.error("EMAIL_FROM not configured. Cannot send email.")
            raise ValueError("EMAIL_FROM not configured")
        
        try:
            # Create MIME message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.config.EMAIL_FROM_NAME} <{self.config.EMAIL_FROM}>"
            message["To"] = to_email
            
            # Attach HTML content
            html_part = MIMEText(html_content, "html")
            message.attach(html_part)
            
            # Connect to SMTP server and send email
            logger.info(f"Connecting to SMTP server: {self.config.SMTP_HOST}:{self.config.SMTP_PORT}")
            
            async with SMTP(
                hostname=self.config.SMTP_HOST,
                port=self.config.SMTP_PORT,
                start_tls=True  # Use STARTTLS for port 587
            ) as smtp:
                # Login to SMTP server
                logger.debug(f"Logging in as: {self.config.SMTP_USERNAME}")
                await smtp.login(self.config.SMTP_USERNAME, self.config.SMTP_PASSWORD)
                
                # Send email
                logger.info(f"Sending email to: {to_email}")
                await smtp.send_message(message)
                
                logger.info(f"Email sent successfully to: {to_email}")
                
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}", exc_info=True)
            raise Exception(f"Failed to send email: {str(e)}")
    
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
        try:
            # Load and render template
            template = self.template_env.get_template("emails/match_notification.html")
            
            # Prepare template context
            # Format created_at - handle both datetime objects and strings
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
            logger.info(f"Sending match notification for product '{product.title}' to {email}")
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
                    Each dict should have: {'product': Product, 'search_request': SearchRequest}
            
        Raises:
            Exception: If email sending fails
        """
        try:
            from datetime import datetime
            
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
            # Format date for template
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
            logger.info(f"Sending daily digest with {match_count} matches to {email}")
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
        try:
            # Load and render template
            template = self.template_env.get_template("emails/search_started.html")
            
            # Build platforms list from boolean fields
            platforms = []
            if search_request.search_craigslist:
                platforms.append("Craigslist")
            if search_request.search_ebay:
                platforms.append("eBay")
            if search_request.search_facebook:
                platforms.append("Facebook Marketplace")
            
            # Prepare template context
            # Format created_at - handle both datetime objects and strings
            created_at_str = "Just now"
            if search_request.created_at:
                try:
                    if isinstance(search_request.created_at, str):
                        created_at_str = search_request.created_at
                    elif hasattr(search_request.created_at, 'strftime'):
                        created_at_str = search_request.created_at.strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        # Fallback: convert to string
                        created_at_str = str(search_request.created_at)
                except Exception as e:
                    logger.warning(f"Could not format created_at: {e}, using 'Just now'")
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
            logger.info(f"Sending search started confirmation for '{search_request.product_name}' to {email}")
            await self.send_email(
                to_email=email,
                subject=subject,
                html_content=html_content
            )
            
            logger.info(f"Search started confirmation sent successfully to {email}")
            
        except Exception as e:
            logger.error(f"Failed to send search started confirmation to {email}: {str(e)}", exc_info=True)
            raise Exception(f"Failed to send search started confirmation: {str(e)}")



    async def prepare_daily_digest_data(
        self, 
        db: Session
    ) -> Dict[str, List[Dict]]:
        """
        Prepare data for daily digest emails.
        
        Returns:
            Dict mapping email addresses to their matches
        """
        from datetime import datetime, timedelta
        
        # 1. Calculate time range (last 24 hours)
        yesterday = datetime.now() - timedelta(days=1)
        
        # 2. Get all matches from last 24 hours
        recent_matches = db.query(Product).filter(
            Product.created_at >= yesterday,
            Product.is_match == True
        ).all()
        
        # 3. Get all email preferences with digest enabled
        email_prefs = db.query(EmailPreference).filter(
            EmailPreference.include_in_digest == True
        ).all()
        
        # 4. Group matches by email address
        digest_data = {}
        for pref in email_prefs:
            # Get matches for this search request
            matches = [
                m for m in recent_matches 
                if m.search_execution.search_request_id == pref.search_request_id
            ]
            
            if matches:
                if pref.email_address not in digest_data:
                    digest_data[pref.email_address] = []
                
                # Add matches with search request info
                for match in matches:
                    digest_data[pref.email_address].append({
                        'product': match,
                        'search_request': pref.search_request
                    })
        
        return digest_data