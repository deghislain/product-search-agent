# Day 16-17: Email Service - Detailed Implementation Plan

A comprehensive, beginner-friendly guide to implementing the email notification system for the Product Search Agent.

---

## 📋 Overview

**Duration:** 10 hours (2 days)  
**Difficulty:** Intermediate  
**Prerequisites:** 
- Days 1-15 completed
- Basic understanding of HTML
- Gmail account for SMTP

---

## 🎯 What You'll Build

An email notification system that:
1. Sends beautiful HTML emails when products match search criteria
2. Sends daily digest emails summarizing all matches
3. Sends confirmation emails when searches start
4. Allows users to configure email preferences

---

## 🏗️ Architecture & Design Patterns

### Design Patterns Used

#### 1. **Service Pattern** (Main Pattern)
**What it is:** Encapsulates business logic in a dedicated service class, separating it from API routes and models.

**Why we use it:**
- Keeps email logic in one place
- Easy to test independently
- Can be reused across different parts of the application
- Makes code more maintainable

**Example:**
```python
# Instead of putting email logic in routes:
@app.post("/send-email")
def send_email():
    # Email logic here... (BAD)

# We create a service:
class EmailService:
    def send_match_notification(self, ...):
        # Email logic here (GOOD)
```

#### 2. **Template Pattern**
**What it is:** Uses HTML templates with placeholders that get filled with actual data.

**Why we use it:**
- Separates email design from email logic
- Easy to update email appearance without changing code
- Reusable templates for different emails

**Example:**
```html
<!-- Template with placeholders -->
<h1>Hello {{user_name}}!</h1>
<p>Found {{product_count}} matches</p>
```

#### 3. **Dependency Injection**
**What it is:** Pass dependencies (like configuration) to a class instead of creating them inside.

**Why we use it:**
- Easy to test (can inject mock objects)
- Flexible configuration
- Follows SOLID principles

**Example:**
```python
# Instead of:
class EmailService:
    def __init__(self):
        self.smtp_host = "smtp.gmail.com"  # Hard-coded (BAD)

# We inject configuration:
class EmailService:
    def __init__(self, config: Settings):
        self.smtp_host = config.smtp_host  # Injected (GOOD)
```

---

## 📝 Sub-Tasks Breakdown

### **Sub-Task 1: Setup Email Configuration** (1 hour)

#### What You'll Do:
Add email-related settings to your configuration file.

#### Steps:

1. **Update `backend/app/config.py`:**
   - Add SMTP server settings
   - Add email credentials
   - Add email preferences

2. **Create Gmail App Password:**
   - Go to Google Account settings
   - Enable 2-factor authentication
   - Generate an "App Password" for your application
   - Save this password securely

3. **Update `.env` file:**
   - Add your Gmail credentials
   - Add SMTP configuration

#### Code Example:
```python
# In config.py
class Settings(BaseSettings):
    # ... existing settings ...
    
    # Email Configuration
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USERNAME: str = ""  # Your Gmail address
    SMTP_PASSWORD: str = ""  # App password
    EMAIL_FROM: str = ""  # Sender email
    EMAIL_FROM_NAME: str = "Product Search Agent"
    
    # Email Features
    ENABLE_EMAIL_NOTIFICATIONS: bool = True
    DAILY_DIGEST_TIME: str = "09:00"  # 9 AM
```

#### Deliverable:
- ✅ Configuration updated with email settings
- ✅ Gmail app password generated
- ✅ `.env` file updated

---

### **Sub-Task 2: Create Database Model for Email Preferences** (1.5 hours)

#### What You'll Do:
Add a table to store user email preferences (which notifications they want to receive).

#### Steps:

1. **Create new model file: `backend/app/models/email_preference.py`**

2. **Define the EmailPreference model:**
   - Link to search requests
   - Store notification preferences
   - Store email address

3. **Update database initialization**

#### Code Structure:
```python
class EmailPreference(Base):
    __tablename__ = "email_preferences"
    
    id: int (primary key)
    search_request_id: int (foreign key)
    email_address: str
    notify_on_match: bool (send email when match found)
    notify_on_start: bool (send email when search starts)
    include_in_digest: bool (include in daily digest)
    created_at: datetime
    updated_at: datetime
```

#### Deliverable:
- ✅ EmailPreference model created
- ✅ Database migration applied
- ✅ Pydantic schema created

---

### **Sub-Task 3: Create HTML Email Templates** (2 hours)

#### What You'll Do:
Design beautiful, responsive HTML email templates using Jinja2.

#### Steps:

1. **Create templates directory:**
   ```bash
   mkdir -p backend/app/templates/emails
   ```

2. **Create base template: `base.html`**
   - Common header/footer
   - Styling
   - Responsive design

3. **Create specific templates:**
   - `match_notification.html` - When a product matches
   - `daily_digest.html` - Daily summary of all matches
   - `search_started.html` - Confirmation when search begins

#### Template Structure:

**Base Template (`base.html`):**
```html
<!DOCTYPE html>
<html>
<head>
    <style>
        /* Inline CSS for email compatibility */
        body { font-family: Arial, sans-serif; }
        .container { max-width: 600px; margin: 0 auto; }
        .header { background: #4F46E5; color: white; padding: 20px; }
        .content { padding: 20px; }
        .footer { background: #F3F4F6; padding: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 Product Search Agent</h1>
        </div>
        <div class="content">
            {% block content %}{% endblock %}
        </div>
        <div class="footer">
            <p>Manage your preferences in the dashboard</p>
        </div>
    </div>
</body>
</html>
```

**Match Notification Template:**
```html
{% extends "base.html" %}
{% block content %}
    <h2>New Match Found! 🎉</h2>
    <p>We found a product matching your search: <strong>{{ search_query }}</strong></p>
    
    <div class="product-card">
        <h3>{{ product.title }}</h3>
        <p><strong>Price:</strong> ${{ product.price }}</p>
        <p><strong>Platform:</strong> {{ product.platform }}</p>
        <p><strong>Match Score:</strong> {{ product.match_score }}%</p>
        <a href="{{ product.url }}">View Product</a>
    </div>
{% endblock %}
```

#### Deliverable:
- ✅ Base template created
- ✅ All 3 email templates created
- ✅ Templates tested for rendering

---

### **Sub-Task 4: Implement Email Service Class** (3 hours)

#### What You'll Do:
Create the core email service that handles sending emails.

#### Steps:

1. **Create `backend/app/services/email_service.py`**

2. **Implement EmailService class with methods:**
   - `send_email()` - Core method to send any email
   - `send_match_notification()` - Send match alert
   - `send_daily_digest()` - Send daily summary
   - `send_search_started()` - Send confirmation

3. **Add error handling and logging**

#### Class Structure:
```python
from aiosmtplib import SMTP
from jinja2 import Environment, FileSystemLoader
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailService:
    def __init__(self, config: Settings):
        """Initialize email service with configuration"""
        self.config = config
        self.template_env = Environment(
            loader=FileSystemLoader("app/templates/emails")
        )
    
    async def send_email(
        self, 
        to_email: str, 
        subject: str, 
        html_content: str
    ):
        """Core method to send email via SMTP"""
        # Create message
        # Connect to SMTP server
        # Send email
        # Handle errors
    
    async def send_match_notification(
        self, 
        email: str, 
        product: Product, 
        search_request: SearchRequest
    ):
        """Send notification when product matches"""
        # Load template
        # Render with product data
        # Send email
    
    async def send_daily_digest(
        self, 
        email: str, 
        matches: List[Product]
    ):
        """Send daily summary of all matches"""
        # Group matches by search request
        # Load template
        # Render with all matches
        # Send email
    
    async def send_search_started(
        self, 
        email: str, 
        search_request: SearchRequest
    ):
        """Send confirmation when search starts"""
        # Load template
        # Render with search details
        # Send email
```

#### Key Concepts:

**Async/Await:**
- Email sending can be slow (network operation)
- Using `async` allows other code to run while waiting
- Don't block the main application

**SMTP (Simple Mail Transfer Protocol):**
- Standard protocol for sending emails
- Gmail uses: smtp.gmail.com:587
- Requires authentication (username/password)

**MIME (Multipurpose Internet Mail Extensions):**
- Format for email messages
- Supports HTML content
- Can include attachments

#### Deliverable:
- ✅ EmailService class implemented
- ✅ All methods working
- ✅ Error handling added
- ✅ Logging configured

---

### **Sub-Task 5: Create Email Service Tests** (1.5 hours)

#### What You'll Do:
Write tests to ensure email service works correctly.

#### Steps:

1. **Create `backend/app/tests/test_email_service.py`**

2. **Write tests for:**
   - Template rendering
   - Email sending (with mock SMTP)
   - Error handling
   - Each email type

#### Test Structure:
```python
import pytest
from unittest.mock import Mock, patch
from app.services.email_service import EmailService

@pytest.fixture
def email_service():
    """Create email service for testing"""
    config = Mock()
    config.SMTP_HOST = "smtp.gmail.com"
    config.SMTP_PORT = 587
    return EmailService(config)

def test_template_rendering(email_service):
    """Test that templates render correctly"""
    # Test template with sample data
    # Assert output contains expected content

@patch('aiosmtplib.SMTP')
async def test_send_email(mock_smtp, email_service):
    """Test email sending with mocked SMTP"""
    # Mock SMTP connection
    # Call send_email
    # Assert SMTP methods were called correctly

async def test_send_match_notification(email_service):
    """Test match notification email"""
    # Create sample product and search request
    # Call send_match_notification
    # Assert email was sent with correct content
```

#### Deliverable:
- ✅ Test file created
- ✅ All tests passing
- ✅ Coverage > 80%

---

### **Sub-Task 6: Integrate with Orchestrator** (1 hour)

#### What You'll Do:
Connect the email service to the search orchestrator so emails are sent automatically when matches are found.

#### Steps:

1. **Update `backend/app/core/orchestrator.py`:**
   - Import EmailService
   - Initialize email service
   - Call email service when matches found

2. **Add email notification logic:**
   - Check if email notifications enabled
   - Get email preferences from database
   - Send email for each match

#### Code Example:
```python
class SearchOrchestrator:
    def __init__(self, db: Session):
        self.db = db
        self.email_service = EmailService(settings)
    
    async def execute_search(self, search_request_id: int):
        # ... existing search logic ...
        
        # After finding matches:
        if matches:
            # Get email preferences
            email_pref = self.db.query(EmailPreference).filter(
                EmailPreference.search_request_id == search_request_id
            ).first()
            
            # Send notifications if enabled
            if email_pref and email_pref.notify_on_match:
                for match in matches:
                    await self.email_service.send_match_notification(
                        email=email_pref.email_address,
                        product=match,
                        search_request=search_request
                    )
```

#### Deliverable:
- ✅ Orchestrator updated
- ✅ Email notifications sent on matches
- ✅ Integration tested

---

### **Sub-Task 7: Add API Endpoints for Email Preferences** (1 hour)

#### What You'll Do:
Create API endpoints to manage email preferences.

#### Steps:

1. **Create `backend/app/api/routes/email_preferences.py`**

2. **Implement endpoints:**
   - `POST /api/email-preferences` - Create preferences
   - `GET /api/email-preferences/{search_request_id}` - Get preferences
   - `PUT /api/email-preferences/{id}` - Update preferences
   - `DELETE /api/email-preferences/{id}` - Delete preferences

#### Endpoint Example:
```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/email-preferences", tags=["email"])

@router.post("/")
def create_email_preference(
    preference: EmailPreferenceCreate,
    db: Session = Depends(get_db)
):
    """Create email notification preferences"""
    db_preference = EmailPreference(**preference.dict())
    db.add(db_preference)
    db.commit()
    return db_preference

@router.get("/{search_request_id}")
def get_email_preference(
    search_request_id: int,
    db: Session = Depends(get_db)
):
    """Get email preferences for a search request"""
    return db.query(EmailPreference).filter(
        EmailPreference.search_request_id == search_request_id
    ).first()
```

#### Deliverable:
- ✅ API endpoints created
- ✅ CRUD operations working
- ✅ Endpoints tested with Postman/curl

---

## 🧪 Testing Your Implementation

### Manual Testing Steps:

1. **Test Email Configuration:**
   ```bash
   # Start the application
   uvicorn app.main:app --reload
   
   # Check logs for email service initialization
   ```

2. **Test Template Rendering:**
   ```python
   # In Python shell
   from app.services.email_service import EmailService
   service = EmailService(settings)
   # Test template rendering
   ```

3. **Test Email Sending:**
   - Create a search request with email preferences
   - Trigger a search manually
   - Check your email inbox for notifications

4. **Test Each Email Type:**
   - Match notification: Trigger a search with matches
   - Search started: Create a new search request
   - Daily digest: Wait for scheduled time or trigger manually

### Automated Testing:
```bash
# Run all email service tests
pytest app/tests/test_email_service.py -v

# Run with coverage
pytest app/tests/test_email_service.py --cov=app.services.email_service
```

---

## 🔧 Troubleshooting Guide

### Common Issues:

#### Issue 1: "Authentication failed" error
**Cause:** Wrong Gmail credentials or app password not generated  
**Solution:**
1. Verify Gmail address in `.env`
2. Generate new app password in Google Account settings
3. Use app password, not regular password

#### Issue 2: Emails not sending
**Cause:** SMTP connection blocked or wrong port  
**Solution:**
1. Check firewall settings
2. Verify SMTP port (587 for TLS)
3. Try port 465 for SSL
4. Check Gmail "Less secure app access" settings

#### Issue 3: Templates not found
**Cause:** Wrong template path  
**Solution:**
1. Verify templates directory exists: `backend/app/templates/emails/`
2. Check template file names match code
3. Verify Jinja2 loader path

#### Issue 4: HTML not rendering in email
**Cause:** Email client doesn't support HTML or CSS issues  
**Solution:**
1. Use inline CSS (not external stylesheets)
2. Test with multiple email clients
3. Use email-safe HTML (tables for layout)

---

## 📚 Key Concepts Explained

### 1. SMTP (Simple Mail Transfer Protocol)
- **What:** Protocol for sending emails over the internet
- **How:** Client connects to SMTP server, authenticates, sends message
- **Ports:** 
  - 587: TLS (recommended)
  - 465: SSL
  - 25: Unencrypted (not recommended)

### 2. Jinja2 Templates
- **What:** Template engine for Python
- **Syntax:**
  - `{{ variable }}` - Insert variable
  - `{% for item in items %}` - Loop
  - `{% if condition %}` - Conditional
  - `{% extends "base.html" %}` - Template inheritance

### 3. Async Email Sending
- **Why:** Email sending is slow (network I/O)
- **Benefit:** Don't block application while sending
- **How:** Use `async`/`await` keywords

### 4. MIME Messages
- **What:** Standard format for email messages
- **Parts:**
  - Headers (From, To, Subject)
  - Body (Text and/or HTML)
  - Attachments (optional)

---

## ✅ Completion Checklist

- [ ] **Sub-Task 1:** Email configuration setup
  - [ ] Config.py updated
  - [ ] Gmail app password generated
  - [ ] .env file configured

- [ ] **Sub-Task 2:** Database model created
  - [ ] EmailPreference model implemented
  - [ ] Database migrated
  - [ ] Schema created

- [ ] **Sub-Task 3:** HTML templates created
  - [ ] Base template
  - [ ] Match notification template
  - [ ] Daily digest template
  - [ ] Search started template

- [ ] **Sub-Task 4:** Email service implemented
  - [ ] EmailService class created
  - [ ] All methods working
  - [ ] Error handling added

- [ ] **Sub-Task 5:** Tests written
  - [ ] Test file created
  - [ ] All tests passing
  - [ ] Coverage > 80%

- [ ] **Sub-Task 6:** Orchestrator integration
  - [ ] Email service integrated
  - [ ] Notifications sent on matches
  - [ ] Integration tested

- [ ] **Sub-Task 7:** API endpoints created
  - [ ] CRUD endpoints implemented
  - [ ] Endpoints tested
  - [ ] Documentation updated

---

## 🎯 Success Criteria

Your Day 16-17 implementation is complete when:

1. ✅ Email service sends emails successfully
2. ✅ All 3 email templates render correctly
3. ✅ Gmail SMTP connection works
4. ✅ Email preferences stored in database
5. ✅ Emails sent automatically when matches found
6. ✅ API endpoints for preferences working
7. ✅ All tests passing
8. ✅ No errors in logs

---

## 📖 Additional Resources

**Email Development:**
- [aiosmtplib Documentation](https://aiosmtplib.readthedocs.io/)
- [Jinja2 Documentation](https://jinja.palletsprojects.com/)
- [Email HTML Best Practices](https://www.campaignmonitor.com/css/)

**Gmail SMTP:**
- [Gmail SMTP Settings](https://support.google.com/mail/answer/7126229)
- [App Passwords Guide](https://support.google.com/accounts/answer/185833)

**Testing:**
- [pytest-asyncio](https://pytest-asyncio.readthedocs.io/)
- [unittest.mock](https://docs.python.org/3/library/unittest.mock.html)

---

## 💡 Tips for Success

1. **Start with configuration** - Get SMTP working first before building features
2. **Test templates separately** - Render templates before integrating with email service
3. **Use mock SMTP in tests** - Don't send real emails during testing
4. **Keep templates simple** - Email clients have limited HTML/CSS support
5. **Log everything** - Add detailed logging for debugging
6. **Test with real emails** - Send test emails to yourself
7. **Handle errors gracefully** - Email sending can fail; don't crash the app

---

## 🚀 Next Steps (Day 18)

After completing Day 16-17, you'll move to:
- **Day 18:** Daily Digest Scheduler
- Add scheduled job to send daily digest emails
- Implement digest aggregation logic
- Test scheduled email delivery

---

**Good luck with your email service implementation! 📧**