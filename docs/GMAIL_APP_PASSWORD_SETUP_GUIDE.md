# Gmail App Password Setup Guide

A step-by-step guide to generate an App Password for your Gmail account to use with the Product Search Agent email service.

---

## 🤔 What is an App Password?

**App Password** is a 16-character code that gives an application (like our Product Search Agent) permission to access your Gmail account **without using your actual Gmail password**.

### Why Not Use Your Regular Gmail Password?

1. **Security:** Your real password stays secret
2. **Google Requirement:** Google doesn't allow apps to use regular passwords anymore (for security)
3. **Easy to Revoke:** You can delete the app password anytime without changing your main password
4. **Specific Access:** Each app gets its own password

---

## 📋 Prerequisites

Before you can create an App Password, you need:

1. ✅ A Gmail account (e.g., yourname@gmail.com)
2. ✅ **2-Step Verification enabled** (required by Google)

---

## 🔐 Step-by-Step: Enable 2-Step Verification

If you don't have 2-Step Verification enabled yet, follow these steps:

### Step 1: Go to Google Account Security
1. Open your browser
2. Go to: https://myaccount.google.com/security
3. Sign in with your Gmail account

### Step 2: Find 2-Step Verification
1. Scroll down to "How you sign in to Google"
2. Click on **"2-Step Verification"**

### Step 3: Enable It
1. Click **"Get Started"**
2. Follow the prompts:
   - Enter your password
   - Add your phone number
   - Choose how to receive codes (text message or phone call)
   - Enter the verification code sent to your phone
3. Click **"Turn On"**

✅ **2-Step Verification is now enabled!**

---

## 🔑 Step-by-Step: Generate App Password

Now that 2-Step Verification is enabled, you can create an App Password:

### Step 1: Go to App Passwords Page
1. Go to: https://myaccount.google.com/apppasswords
   - OR go to Google Account → Security → 2-Step Verification → App passwords (at the bottom)
2. You may need to sign in again

### Step 2: Create New App Password
1. You'll see "App passwords" page
2. At the bottom, there's a section called "Select app and device"
3. Click the dropdown under **"Select app"**
4. Choose **"Mail"** (or "Other" if Mail isn't available)

### Step 3: Name Your App
1. If you selected "Other", type a name: **"Product Search Agent"**
2. Click **"Generate"**

### Step 4: Copy Your App Password
1. Google will show you a 16-character password like: `abcd efgh ijkl mnop`
2. **IMPORTANT:** Copy this password immediately!
3. You won't be able to see it again
4. Click **"Done"**

---

## 💾 Where to Use the App Password

### In Your `.env` File

Open your `backend/.env` file and add:

```bash
# Email Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=abcdefghijklmnop  # Your 16-character app password (no spaces!)
EMAIL_FROM=your-email@gmail.com
EMAIL_FROM_NAME=Product Search Agent
```

**Important Notes:**
- Remove all spaces from the app password (Google shows it with spaces, but you need to remove them)
- Example: `abcd efgh ijkl mnop` becomes `abcdefghijklmnop`
- Use your actual Gmail address for `SMTP_USERNAME` and `EMAIL_FROM`

---

## 🧪 Test Your Setup

After adding the app password to your `.env` file, test it:

### Quick Test Script

Create a file `backend/test_email.py`:

```python
import asyncio
from aiosmtplib import SMTP
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

async def test_email():
    # Get credentials from .env
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = int(os.getenv("SMTP_PORT"))
    smtp_username = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD")
    
    print(f"Testing email with:")
    print(f"  Host: {smtp_host}")
    print(f"  Port: {smtp_port}")
    print(f"  Username: {smtp_username}")
    print(f"  Password: {'*' * len(smtp_password)}")
    
    # Create test message
    message = MIMEMultipart()
    message["From"] = smtp_username
    message["To"] = smtp_username  # Send to yourself
    message["Subject"] = "Test Email from Product Search Agent"
    
    body = "If you receive this, your email setup is working! 🎉"
    message.attach(MIMEText(body, "plain"))
    
    try:
        # Connect and send
        async with SMTP(hostname=smtp_host, port=smtp_port) as smtp:
            await smtp.connect()
            await smtp.starttls()
            await smtp.login(smtp_username, smtp_password)
            await smtp.send_message(message)
        
        print("✅ Email sent successfully!")
        print(f"Check your inbox at {smtp_username}")
        
    except Exception as e:
        print(f"❌ Error sending email: {e}")

if __name__ == "__main__":
    asyncio.run(test_email())
```

### Run the Test

```bash
cd backend
python test_email.py
```

**Expected Output:**
```
Testing email with:
  Host: smtp.gmail.com
  Port: 587
  Username: your-email@gmail.com
  Password: ****************
✅ Email sent successfully!
Check your inbox at your-email@gmail.com
```

Check your Gmail inbox - you should receive the test email!

---

## 🔧 Troubleshooting

### Error: "Username and Password not accepted"

**Causes:**
1. App password has spaces in it
2. Wrong Gmail address
3. 2-Step Verification not enabled
4. Typo in app password

**Solutions:**
1. Remove all spaces from app password in `.env`
2. Verify your Gmail address is correct
3. Check 2-Step Verification is enabled: https://myaccount.google.com/security
4. Generate a new app password and try again

### Error: "Connection refused" or "Timeout"

**Causes:**
1. Wrong SMTP port
2. Firewall blocking connection
3. Wrong SMTP host

**Solutions:**
1. Use port `587` (TLS) or `465` (SSL)
2. Check firewall settings
3. Verify `SMTP_HOST=smtp.gmail.com`

### Error: "App passwords" option not showing

**Cause:** 2-Step Verification not enabled

**Solution:**
1. Enable 2-Step Verification first (see above)
2. Wait a few minutes
3. Try accessing https://myaccount.google.com/apppasswords again

### Can't Find App Passwords Page

**Alternative Method:**
1. Go to: https://myaccount.google.com/
2. Click "Security" in the left sidebar
3. Scroll to "How you sign in to Google"
4. Click "2-Step Verification"
5. Scroll to the bottom
6. Click "App passwords"

---

## 🔒 Security Best Practices

### DO:
✅ Keep your app password secret (like a regular password)
✅ Store it only in your `.env` file
✅ Add `.env` to `.gitignore` (never commit it to Git)
✅ Use different app passwords for different applications
✅ Revoke app passwords you're not using

### DON'T:
❌ Share your app password with anyone
❌ Commit your `.env` file to Git
❌ Use your regular Gmail password in the app
❌ Reuse the same app password across multiple apps

---

## 🗑️ How to Revoke an App Password

If you need to revoke (delete) an app password:

1. Go to: https://myaccount.google.com/apppasswords
2. You'll see a list of all your app passwords
3. Find "Product Search Agent" (or whatever you named it)
4. Click the **trash icon** next to it
5. Confirm deletion

The app will immediately stop working with that password.

---

## 📝 Quick Reference

### What You Need:

| Setting | Value | Where to Get It |
|---------|-------|-----------------|
| `SMTP_HOST` | `smtp.gmail.com` | Fixed value |
| `SMTP_PORT` | `587` | Fixed value (TLS) |
| `SMTP_USERNAME` | Your Gmail address | Your Gmail account |
| `SMTP_PASSWORD` | 16-character code | Generate at https://myaccount.google.com/apppasswords |
| `EMAIL_FROM` | Your Gmail address | Same as SMTP_USERNAME |

### Example `.env` Configuration:

```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=john.doe@gmail.com
SMTP_PASSWORD=abcdefghijklmnop
EMAIL_FROM=john.doe@gmail.com
EMAIL_FROM_NAME=Product Search Agent
```

---

## 🎯 Summary

1. **Enable 2-Step Verification** on your Google Account
2. **Generate an App Password** at https://myaccount.google.com/apppasswords
3. **Copy the 16-character password** (remove spaces)
4. **Add it to your `.env` file** as `SMTP_PASSWORD`
5. **Test it** with the test script
6. **Keep it secure** - never commit to Git!

---

## 🆘 Still Having Issues?

If you're still stuck:

1. **Double-check** all steps above
2. **Try generating a new app password** (delete the old one first)
3. **Verify your Gmail account** is working normally
4. **Check Google Account security settings** for any blocks
5. **Try the test script** to see the exact error message

---

## 📚 Additional Resources

- [Google App Passwords Help](https://support.google.com/accounts/answer/185833)
- [2-Step Verification Help](https://support.google.com/accounts/answer/185839)
- [Gmail SMTP Settings](https://support.google.com/mail/answer/7126229)

---

**You're now ready to use Gmail with your Product Search Agent! 📧✨**