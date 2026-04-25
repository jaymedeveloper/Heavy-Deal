import yagmail

# Gmail Configuration
SENDER_EMAIL = "heavydeals567@gmail.com"
SENDER_PASSWORD = "xqsj qywl oaqh xajc"  # ✅ Apna app password yahan daalo

def send_email(to_email, subject, message, is_html=False):
    """
    Common function to send email
    
    Parameters:
    to_email (str): Receiver email address
    subject (str): Email subject
    message (str): Email body/content (plain text or HTML)
    is_html (bool): True if message is HTML, False for plain text
    
    Returns:
    tuple: (success: bool, response: str)
    """
    try:
        yag = yagmail.SMTP(SENDER_EMAIL, SENDER_PASSWORD)
        yag.send(to=to_email, subject=subject, contents=message)
        return True, "Email sent successfully"
    except Exception as e:
        return False, str(e)


def send_welcome_email(to_email, buyer_name):
    """
    Welcome email for new user
    """
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; }}
            .container {{ max-width: 600px; margin: 0 auto; background: white; }}
            .header {{ background: linear-gradient(135deg, #0a192f, #112240); padding: 30px; text-align: center; }}
            .header h1 {{ color: #f97316; margin: 0; }}
            .content {{ padding: 30px; }}
            .steps {{ display: flex; justify-content: space-between; margin: 30px 0; }}
            .step {{ text-align: center; flex: 1; }}
            .step-number {{ background: #f97316; width: 30px; height: 30px; border-radius: 50%; display: inline-block; line-height: 30px; color: white; font-weight: bold; margin-bottom: 10px; }}
            .button {{ background: #f97316; color: white; padding: 12px 24px; text-decoration: none; border-radius: 40px; display: inline-block; }}
            .footer {{ background: #f8fafc; padding: 20px; text-align: center; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎉 HeavyDeals</h1>
                <p style="color: white;">Welcome Aboard!</p>
            </div>
            <div class="content">
                <h2>Welcome {buyer_name}! 👋</h2>
                <p>We're excited to have you on HeavyDeals - India's trusted review mediation platform.</p>
                
                <div class="steps">
                    <div class="step">
                        <div class="step-number">1</div>
                        <strong>Order</strong><br>
                        <small>Place orders on Amazon</small>
                    </div>
                    <div class="step">
                        <div class="step-number">2</div>
                        <strong>Review</strong><br>
                        <small>Submit honest reviews</small>
                    </div>
                    <div class="step">
                        <div class="step-number">3</div>
                        <strong>Earn</strong><br>
                        <small>Get rewarded! 💰</small>
                    </div>
                </div>
                
                <div style="text-align: center;">
                    <a href="https://heavy-deal-a5in.onrender.com/buyer/dashboard" class="button">🚀 Start Earning Now</a>
                </div>
            </div>
            <div class="footer">
                <p>Have questions? Reach out to heavydeals567@gmail.com</p>
            </div>
        </div>
    </body>
    </html>
    """
    return send_email(to_email, f"Welcome to HeavyDeals! 🎉 - {buyer_name}", html_content, is_html=True)
