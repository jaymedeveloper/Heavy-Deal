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
    Welcome email for new user - Inline CSS version (FINAL)
    """
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Welcome to HeavyDeals</title>
    </head>
    <body style="margin:0; padding:0; font-family: Arial, sans-serif; background-color: #f0f2f5;">
        <div style="max-width: 550px; margin: 20px auto; background: #ffffff; border-radius: 24px; overflow: hidden;">
            
            <!-- Header -->
            <div style="background: linear-gradient(135deg, #0a192f, #112240); padding: 30px; text-align: center;">
                <div style="width: 70px; height: 70px; background: #f97316; border-radius: 18px; display: inline-flex; align-items: center; justify-content: center; margin-bottom: 15px;">
                    <span style="font-size: 36px;">🛍️</span>
                </div>
                <h1 style="color: #f97316; margin: 0; font-size: 28px;">HeavyDeals</h1>
                <p style="color: #94a3b8; margin: 8px 0 0;">Earn Rewards for Reviews</p>
            </div>
            
            <!-- Content -->
            <div style="padding: 30px 25px;">
                <h2 style="color: #0a192f; margin: 0 0 10px;">Welcome, {buyer_name}! 🎉</h2>
                <p style="color: #64748b; line-height: 1.5;">We're thrilled to have you on board. Get ready to earn rewards for your honest reviews!</p>
                
                <!-- Bonus -->
                <div style="background: #ffedd5; border-radius: 16px; padding: 20px; text-align: center; margin: 25px 0;">
                    <p style="color: #0a192f; font-weight: bold; margin: 0 0 5px;">✨ First Order Bonus</p>
                    <p style="color: #f97316; font-size: 28px; font-weight: bold; margin: 0;">UP TO ₹500 EXTRA</p>
                </div>
                
                <!-- Steps -->
                <h3 style="color: #0a192f; text-align: center;">⚡ How It Works</h3>
                <div style="display: flex; gap: 10px; margin: 20px 0;">
                    <div style="flex: 1; background: #f8fafc; border-radius: 12px; padding: 15px; text-align: center;">
                        <div style="font-size: 24px;">📦</div>
                        <strong>Step 1</strong><br>
                        <small>Order on Amazon</small>
                    </div>
                    <div style="flex: 1; background: #f8fafc; border-radius: 12px; padding: 15px; text-align: center;">
                        <div style="font-size: 24px;">⭐</div>
                        <strong>Step 2</strong><br>
                        <small>Submit Review</small>
                    </div>
                    <div style="flex: 1; background: #f8fafc; border-radius: 12px; padding: 15px; text-align: center;">
                        <div style="font-size: 24px;">💰</div>
                        <strong>Step 3</strong><br>
                        <small>Get Paid</small>
                    </div>
                </div>
                
                <!-- Benefits -->
                <div style="background: #f0fdf4; border-radius: 12px; padding: 15px; margin: 20px 0;">
                    <p style="color: #16a34a; font-weight: bold; margin: 0 0 10px;">🎁 What You Get</p>
                    <p>✅ 50% refund on every review</p>
                    <p>✅ Bonus for first 5 orders</p>
                    <p>✅ Priority support</p>
                </div>
                
                <!-- Button -->
                <div style="text-align: center; margin: 25px 0;">
                    <a href="https://heavy-deal-a5in.onrender.com/buyer/dashboard" style="background: #f97316; color: white; padding: 12px 30px; text-decoration: none; border-radius: 50px; display: inline-block;">🚀 Start Earning Now</a>
                </div>
                
                <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 20px 0;">
                
                <p style="text-align: center; font-size: 12px; color: #64748b;">
                    Need help? <a href="mailto:heavydeals567@gmail.com" style="color: #f97316;">heavydeals567@gmail.com</a>
                </p>
            </div>
            
            <!-- Footer -->
            <div style="background: #f8fafc; padding: 20px; text-align: center; border-top: 1px solid #e2e8f0;">
                <p style="font-size: 11px; color: #64748b;">© 2024 HeavyDeals - Earn Rewards for Honest Reviews</p>
                <p style="font-size: 11px; color: #64748b;">This is an automated message, please do not reply.</p>
            </div>
            
        </div>
    </body>
    </html>
    """
    return send_email(to_email, f"Welcome to HeavyDeals! 🎉 Start Earning Rewards Today", html_content, is_html=True)
