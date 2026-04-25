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
    Welcome email for new user - Email client friendly version
    """
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Welcome to HeavyDeals</title>
    </head>
    <body style="margin:0; padding:0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f0f2f5;">
        
        <!-- Main Container -->
        <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: #f0f2f5; padding: 20px;">
            <tr>
                <td align="center">
                    <table width="100%" cellpadding="0" cellspacing="0" border="0" style="max-width: 550px; width: 100%; background: #ffffff; border-radius: 24px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
                        
                        <!-- Header -->
                        <tr>
                            <td style="background: linear-gradient(135deg, #0a192f, #112240); padding: 30px 20px; text-align: center;">
                                <table width="100%" cellpadding="0" cellspacing="0" border="0">
                                    <tr>
                                        <td align="center">
                                            <div style="width: 70px; height: 70px; background: #f97316; border-radius: 18px; display: inline-flex; align-items: center; justify-content: center; margin-bottom: 15px;">
                                                <span style="font-size: 36px;">🛍️</span>
                                            </div>
                                            <h1 style="color: #f97316; margin: 0; font-size: 28px; font-weight: 800;">HeavyDeals</h1>
                                            <p style="color: #94a3b8; margin: 8px 0 0; font-size: 13px;">India's Trusted Review Platform</p>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                        
                        <!-- Content -->
                        <tr>
                            <td style="padding: 30px 25px;">
                                
                                <!-- Greeting -->
                                <h2 style="color: #0a192f; font-size: 22px; margin: 0 0 10px;">Welcome, {buyer_name}! 🎉</h2>
                                <p style="color: #64748b; font-size: 15px; line-height: 1.5; margin: 0 0 25px;">We're thrilled to have you on board. Get ready to earn rewards for your honest reviews!</p>
                                
                                <!-- Bonus Box -->
                                <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background: #ffedd5; border-radius: 16px; margin-bottom: 25px;">
                                    <tr>
                                        <td style="padding: 20px; text-align: center;">
                                            <p style="color: #0a192f; font-size: 16px; font-weight: 600; margin: 0 0 5px;">✨ First Order Bonus</p>
                                            <p style="color: #f97316; font-size: 28px; font-weight: 800; margin: 0;">UP TO ₹500 EXTRA</p>
                                            <p style="color: #64748b; font-size: 12px; margin: 10px 0 0;">Complete your first order today</p>
                                        </td>
                                    </tr>
                                </table>
                                
                                <!-- How It Works -->
                                <h3 style="color: #0a192f; font-size: 18px; text-align: center; margin: 0 0 20px;">⚡ How It Works</h3>
                                
                                <table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom: 25px;">
                                    <tr>
                                        <!-- Step 1 -->
                                        <td width="33%" style="text-align: center; padding: 0 5px;">
                                            <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background: #f8fafc; border-radius: 12px; padding: 15px 10px;">
                                                <tr><td align="center"><div style="background: #f97316; width: 40px; height: 40px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; margin-bottom: 10px;"><span style="font-size: 20px;">📦</span></div></td></tr>
                                                <tr><td align="center"><strong style="color: #0a192f; font-size: 14px;">Step 1</strong></td></tr>
                                                <tr><td align="center"><small style="color: #64748b; font-size: 11px;">Order on Amazon</small></td></tr>
                                            </table>
                                        </td>
                                        <!-- Step 2 -->
                                        <td width="33%" style="text-align: center; padding: 0 5px;">
                                            <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background: #f8fafc; border-radius: 12px; padding: 15px 10px;">
                                                <tr><td align="center"><div style="background: #f97316; width: 40px; height: 40px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; margin-bottom: 10px;"><span style="font-size: 20px;">⭐</span></div></td></tr>
                                                <tr><td align="center"><strong style="color: #0a192f; font-size: 14px;">Step 2</strong></td></tr>
                                                <tr><td align="center"><small style="color: #64748b; font-size: 11px;">Submit Review</small></td></tr>
                                            </table>
                                        </td>
                                        <!-- Step 3 -->
                                        <td width="33%" style="text-align: center; padding: 0 5px;">
                                            <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background: #f8fafc; border-radius: 12px; padding: 15px 10px;">
                                                <tr><td align="center"><div style="background: #f97316; width: 40px; height: 40px; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; margin-bottom: 10px;"><span style="font-size: 20px;">💰</span></div></td></tr>
                                                <tr><td align="center"><strong style="color: #0a192f; font-size: 14px;">Step 3</strong></td></tr>
                                                <tr><td align="center"><small style="color: #64748b; font-size: 11px;">Get Paid</small></td></tr>
                                            </table>
                                        </td>
                                    </tr>
                                </table>
                                
                                <!-- Benefits -->
                                <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background: #f0fdf4; border-radius: 16px; margin-bottom: 25px; border-left: 4px solid #16a34a;">
                                    <tr>
                                        <td style="padding: 20px;">
                                            <h4 style="color: #16a34a; font-size: 16px; margin: 0 0 12px;">🎁 What You Get</h4>
                                            <p style="color: #334155; font-size: 13px; margin: 5px 0;">✅ 50% refund on every successful review</p>
                                            <p style="color: #334155; font-size: 13px; margin: 5px 0;">✅ Bonus rewards for first 5 orders</p>
                                            <p style="color: #334155; font-size: 13px; margin: 5px 0;">✅ Priority support for active reviewers</p>
                                            <p style="color: #334155; font-size: 13px; margin: 5px 0;">✅ Early access to new products</p>
                                        </td>
                                    </tr>
                                </table>
                                
                                <!-- Pro Tip -->
                                <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background: #fef3c7; border-radius: 12px; margin-bottom: 25px;">
                                    <tr>
                                        <td style="padding: 15px;">
                                            <p style="color: #d97706; font-size: 13px; margin: 0;"><strong>💡 Pro Tip:</strong> Submit high-quality screenshots and detailed reviews for faster approval!</p>
                                        </td>
                                    </tr>
                                </table>
                                
                                <!-- CTA Button -->
                                <table width="100%" cellpadding="0" cellspacing="0" border="0">
                                    <tr>
                                        <td align="center">
                                            <a href="https://heavy-deal-a5in.onrender.com/buyer/dashboard" style="display: inline-block; background: linear-gradient(135deg, #f97316, #ea580c); color: white; text-decoration: none; padding: 14px 30px; border-radius: 50px; font-weight: 600; font-size: 15px; margin: 10px 0;">🚀 Start Earning Now</a>
                                        </td>
                                    </tr>
                                </table>
                                
                                <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 25px 0;">
                                
                                <!-- Contact -->
                                <p style="color: #64748b; font-size: 12px; text-align: center; margin: 0;">
                                    📧 Need help? <a href="mailto:heavydeals567@gmail.com" style="color: #f97316; text-decoration: none;">heavydeals567@gmail.com</a>
                                </p>
                                
                            </td>
                        </tr>
                        
                        <!-- Footer -->
                        <tr>
                            <td style="background: #f8fafc; padding: 20px; text-align: center; border-top: 1px solid #e2e8f0;">
                                <p style="color: #64748b; font-size: 11px; margin: 5px 0;">© 2024 HeavyDeals - Earn Rewards for Honest Reviews</p>
                                <p style="color: #64748b; font-size: 11px; margin: 5px 0;">This is an automated message, please do not reply.</p>
                                <p style="color: #64748b; font-size: 11px; margin: 5px 0;">
                                    <a href="https://heavy-deal-a5in.onrender.com" style="color: #f97316; text-decoration: none;">Visit Website</a>
                                </p>
                            </td>
                        </tr>
                        
                    </table>
                </td>
            </tr>
        </table>
        
    </body>
    </html>
    """
    return send_email(to_email, f"Welcome to HeavyDeals! 🎉 Start Earning Rewards Today", html_content, is_html=True)
