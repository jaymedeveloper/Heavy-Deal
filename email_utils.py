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
    Welcome email for new user - Ultra compact for mobile
    """
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Welcome to HeavyDeals</title>
    </head>
    <body style="margin:0; padding:0; font-family: Arial, Helvetica, sans-serif; background-color:#f0f2f5;">
        
        <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:#f0f2f5;">
            <tr>
                <td align="center">
                    <table width="450" cellpadding="0" cellspacing="0" border="0" bgcolor="#ffffff" style="background:#ffffff; border-radius:12px; width:100%; max-width:450px;">
                        
                        <!-- Header -->
                        <tr>
                            <td bgcolor="#0a192f" style="background:#0a192f; padding:15px 12px; text-align:center;">
                                <span style="font-size:28px;">🛍️</span>
                                <h1 style="color:#f97316; margin:3px 0 0; font-size:20px;">HeavyDeals</h1>
                                <p style="color:#94a3b8; margin:2px 0 0; font-size:10px;">Earn Rewards for Reviews</p>
                            </td>
                        </tr>
                        
                        <!-- Welcome -->
                        <tr>
                            <td style="padding:12px 12px 8px;">
                                <h2 style="color:#0a192f; margin:0; font-size:18px;">Welcome, {buyer_name}! 🎉</h2>
                                <p style="color:#64748b; margin:5px 0 0; font-size:13px;">Get ready to earn rewards!</p>
                            </td>
                        </tr>
                        
                        <!-- Bonus -->
                        <tr>
                            <td style="padding:0 12px;">
                                <table width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="#ffedd5" style="background:#ffedd5; border-radius:10px;">
                                    <tr><td style="padding:8px; text-align:center;">
                                        <p style="color:#0a192f; margin:0; font-size:12px; font-weight:bold;">✨ First Order Bonus</p>
                                        <p style="color:#f97316; margin:2px 0 0; font-size:18px; font-weight:bold;">UP TO ₹500 EXTRA</p>
                                    </td></td>
                                </table>
                            </td>
                        </tr>
                        
                        <!-- Steps Title -->
                        <tr>
                            <td style="padding:10px 12px 0;">
                                <p style="color:#0a192f; text-align:center; margin:0; font-weight:bold; font-size:13px;">⚡ How It Works</p>
                            </td>
                        </tr>
                        
                        <!-- Steps -->
                        <tr>
                            <td style="padding:8px 12px;">
                                <table width="100%" cellpadding="0" cellspacing="0" border="0">
                                    <tr>
                                        <td width="33%" align="center" style="padding:3px;">
                                            <table width="100%" cellpadding="6" cellspacing="0" border="0" bgcolor="#f8fafc" style="background:#f8fafc; border-radius:8px;">
                                                <tr><td align="center"><span style="font-size:20px;">📦</span><br><span style="font-size:11px;">Order</span></td></tr>
                                            </table>
                                        </td>
                                        <td width="33%" align="center" style="padding:3px;">
                                            <table width="100%" cellpadding="6" cellspacing="0" border="0" bgcolor="#f8fafc" style="background:#f8fafc; border-radius:8px;">
                                                <tr><td align="center"><span style="font-size:20px;">⭐</span><br><span style="font-size:11px;">Review</span></td></tr>
                                            </table>
                                        </td>
                                        <td width="33%" align="center" style="padding:3px;">
                                            <table width="100%" cellpadding="6" cellspacing="0" border="0" bgcolor="#f8fafc" style="background:#f8fafc; border-radius:8px;">
                                                <tr><td align="center"><span style="font-size:20px;">💰</span><br><span style="font-size:11px;">Get Paid</span></td></tr>
                                            </table>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                        
                        <!-- Benefits -->
                        <tr>
                            <td style="padding:0 12px;">
                                <table width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="#f0fdf4" style="background:#f0fdf4; border-radius:8px;">
                                    <tr><td style="padding:8px;">
                                        <p style="color:#16a34a; margin:0 0 5px; font-weight:bold; font-size:12px;">🎁 What You Get</p>
                                        <p style="color:#334155; margin:2px 0; font-size:11px;">✅ 50% refund on every review</p>
                                        <p style="color:#334155; margin:2px 0; font-size:11px;">✅ Bonus for first 5 orders</p>
                                        <p style="color:#334155; margin:2px 0; font-size:11px;">✅ Priority support</p>
                                    </td></tr>
                                </table>
                            </td>
                        </tr>
                        
                        <!-- Pro Tip -->
                        <tr>
                            <td style="padding:8px 12px;">
                                <table width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="#fef3c7" style="background:#fef3c7; border-radius:8px;">
                                    <tr><td style="padding:6px;">
                                        <p style="color:#d97706; margin:0; font-size:10px;"><b>💡 Tip:</b> Quality screenshots = faster approval!</p>
                                    </td></tr>
                                </table>
                            </td>
                        </tr>
                        
                        <!-- Button -->
                        <tr>
                            <td align="center" style="padding:10px 12px 8px;">
                                <a href="https://heavy-deal-a5in.onrender.com/buyer/dashboard" style="display:inline-block; background:#f97316; color:white; text-decoration:none; padding:8px 20px; border-radius:40px; font-weight:bold; font-size:13px;">🚀 Start Earning</a>
                            </td>
                        </tr>
                        
                        <!-- Divider -->
                        <tr><td style="padding:0 12px;"><hr style="margin:5px 0; border:none; border-top:1px solid #e2e8f0;"></td></tr>
                        
                        <!-- Footer -->
                        <tr>
                            <td style="padding:10px 12px 12px; text-align:center;">
                                <p style="color:#64748b; margin:0; font-size:9px;">Need help? <a href="mailto:heavydeals567@gmail.com" style="color:#f97316;">heavydeals567@gmail.com</a></p>
                                <p style="color:#64748b; margin:3px 0 0; font-size:9px;">© HeavyDeals • Earn Rewards</p>
                            </td>
                        </tr>
                        
                    </table>
                </td>
            </tr>
        </table>
        
    </body>
    </html>
    """
    return send_email(to_email, f"Welcome to HeavyDeals! 🎉", html_content, is_html=True)
