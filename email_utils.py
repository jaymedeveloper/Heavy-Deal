import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ============================================================
# ✅ BREVO SMTP CONFIGURATION - APNI DETAILS DALO
# ============================================================

BREVO_SMTP_SERVER = "smtp-relay.brevo.com"
BREVO_SMTP_PORT = 2525  # Render free ke liye 2525
BREVO_SMTP_LOGIN = "a9fa89001@smtp-brevo.com"  # Brevo ne jo diya hai
BREVO_SMTP_KEY = "xsmtpsib-b346a07446819ade66c14611027f68f41a4d44f07c3af4d818283f7d5a11c497-i6f2ElzmRhE6f8E6"  # 🔑 Brevo se generate kiya hua key dalo

# ============================================================
# 📧 SEND EMAIL - SIMPLE FUNCTION
# ============================================================

def send_simple_email(to_email, subject, message):
    """
    Simple email sending function
    
    Parameters:
    - to_email: Receiver email (e.g., "user@gmail.com")
    - subject: Email subject
    - message: Plain text or HTML message
    """
    try:
        msg = MIMEMultipart()
        msg['From'] = f"Heavy-Deals <{BREVO_SMTP_LOGIN}>"
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(message, 'html'))
        
        print(f"📧 Connecting to {BREVO_SMTP_SERVER}:{BREVO_SMTP_PORT}...")
        
        server = smtplib.SMTP(BREVO_SMTP_SERVER, BREVO_SMTP_PORT)
        server.starttls()
        server.login(BREVO_SMTP_LOGIN, BREVO_SMTP_KEY)
        server.send_message(msg)
        server.quit()
        
        print(f"✅ Email sent to {to_email}")
        return True, "Email sent!"
        
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False, str(e)


# ============================================================
# 🧪 TEST FUNCTION - SIRF EK SIMPLE EMAIL
# ============================================================

def test_email(to_email):
    """
    Ek simple test email bhejo - Check karne ke liye
    """
    subject = "✅ Brevo Test - Heavy-Deals"
    
    message = """
    <h2 style="color: #f97316;">✅ SMTP Working!</h2>
    <p>Your Brevo setup is successful.</p>
    <p>Email sent through Port 2525.</p>
    <hr>
    <small>Heavy-Deals | Test Email</small>
    """
    
    return send_simple_email(to_email, subject, message)


# ============================================================
# 🚀 DIRECT RUN - COMMAND LINE SE TEST KARNE KE LIYE
# ============================================================

if __name__ == "__main__":
    print("=" * 40)
    print("Brevo Email Test")
    print("=" * 40)
    
    email = input("Enter email address to send test: ")
    
    success, msg = test_email(email)
    
    if success:
        print(f"\n✅ Test email sent to {email}")
        print("📬 Check your inbox / spam folder")
    else:
        print(f"\n❌ Failed: {msg}")
