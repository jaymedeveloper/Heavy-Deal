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
    Welcome email - Zero margins in all email clients
    """
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Welcome to HeavyDeals</title>
    </head>
    <body style="margin:0; padding:0; -webkit-text-size-adjust:100%; -ms-text-size-adjust:100%; height:100%; background-color:#f0f2f5;">
        
        <!-- Outlook fix for body margins -->
        <table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:0; padding:0; border-collapse:collapse;">
            <tr>
                <td align="center" style="margin:0; padding:0;">
                    
                    <!-- Main container - Gmail fix -->
                    <div style="max-width:500px; width:100%; margin:0 auto; background-color:#ffffff;">
                        
                        <!-- Header -->
                        <div style="background:#0a192f; padding:12px 10px; text-align:center;">
                            <div style="font-size:24px;">🛍️</div>
                            <div style="color:#f97316; font-size:18px; font-weight:bold; margin:2px 0 0;">HeavyDeals</div>
                            <div style="color:#94a3b8; font-size:10px; margin:2px 0 0;">Earn Rewards for Reviews</div>
                        </div>
                        
                        <!-- Welcome -->
                        <div style="padding:8px 10px 4px;">
                            <div style="color:#0a192f; font-size:17px; font-weight:bold;">Welcome, {buyer_name}! 🎉</div>
                            <div style="color:#64748b; font-size:12px; margin:4px 0 0;">Get ready to earn rewards!</div>
                        </div>
                        
                        <!-- Bonus -->
                        <div style="padding:0 10px;">
                            <div style="background:#ffedd5; border-radius:8px; padding:6px; text-align:center;">
                                <div style="color:#0a192f; font-size:11px; font-weight:bold;">✨ First Order Bonus</div>
                                <div style="color:#f97316; font-size:16px; font-weight:bold; margin:2px 0 0;">UP TO ₹500 EXTRA</div>
                            </div>
                        </div>
                        
                        <!-- Steps Title -->
                        <div style="padding:6px 10px 0;">
                            <div style="color:#0a192f; text-align:center; font-weight:bold; font-size:12px;">⚡ How It Works</div>
                        </div>
                        
                        <!-- Steps Row -->
                        <div style="padding:5px 10px; display:flex; justify-content:space-between; gap:5px;">
                            <div style="flex:1; background:#f8fafc; border-radius:6px; padding:4px; text-align:center;">
                                <div style="font-size:18px;">📦</div>
                                <div style="font-size:10px;">Order</div>
                            </div>
                            <div style="flex:1; background:#f8fafc; border-radius:6px; padding:4px; text-align:center;">
                                <div style="font-size:18px;">⭐</div>
                                <div style="font-size:10px;">Review</div>
                            </div>
                            <div style="flex:1; background:#f8fafc; border-radius:6px; padding:4px; text-align:center;">
                                <div style="font-size:18px;">💰</div>
                                <div style="font-size:10px;">Get Paid</div>
                            </div>
                        </div>
                        
                        <!-- Benefits -->
                        <div style="padding:0 10px;">
                            <div style="background:#f0fdf4; border-radius:6px; padding:6px;">
                                <div style="color:#16a34a; font-weight:bold; font-size:11px; margin:0 0 4px;">🎁 What You Get</div>
                                <div style="color:#334155; font-size:10px; margin:2px 0;">✅ 50% refund on every review</div>
                                <div style="color:#334155; font-size:10px; margin:2px 0;">✅ Bonus for first 5 orders</div>
                                <div style="color:#334155; font-size:10px; margin:2px 0;">✅ Priority support</div>
                            </div>
                        </div>
                        
                        <!-- Pro Tip -->
                        <div style="padding:5px 10px;">
                            <div style="background:#fef3c7; border-radius:6px; padding:4px;">
                                <div style="color:#d97706; font-size:9px;"><b>💡 Tip:</b> Quality screenshots = faster approval!</div>
                            </div>
                        </div>
                        
                        <!-- Button -->
                        <div style="padding:8px 10px 5px; text-align:center;">
                            <a href="https://heavy-deal-a5in.onrender.com/buyer/dashboard" style="display:inline-block; background:#f97316; color:#ffffff; text-decoration:none; padding:6px 18px; border-radius:30px; font-weight:bold; font-size:12px;">🚀 Start Earning</a>
                        </div>
                        
                        <!-- Footer -->
                        <div style="padding:5px 10px 8px;">
                            <hr style="margin:5px 0; border:0; border-top:1px solid #e2e8f0;">
                            <div style="color:#64748b; text-align:center; font-size:9px; margin:5px 0 0;">Need help? <a href="mailto:heavydeals567@gmail.com" style="color:#f97316;">heavydeals567@gmail.com</a></div>
                            <div style="color:#64748b; text-align:center; font-size:9px; margin:3px 0 0;">© HeavyDeals • Earn Rewards</div>
                        </div>
                        
                    </div>
                    
                </td>
            </tr>
        </table>
        
    </body>
    </html>
    """
    return send_email(to_email, f"Welcome to HeavyDeals! 🎉", html_content, is_html=True)
