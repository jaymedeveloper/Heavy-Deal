import yagmail

SENDER_EMAIL = "heavydeals567@gmail.com"
SENDER_PASSWORD = "xqsj qywl oaqh xajc"


def send_email(to_email, subject, message, is_html=False):
    try:
        yag = yagmail.SMTP(SENDER_EMAIL, SENDER_PASSWORD)
        yag.send(to=to_email, subject=subject, contents=message)
        return True, "Email sent successfully"
    except Exception as e:
        return False, str(e)


def send_welcome_email(to_email, buyer_name):
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Welcome</title>
    </head>

    <body style="margin:0; padding:0; background:#0a192f;">

    <!-- PREHEADER -->
    <div style="display:none; max-height:0; overflow:hidden; opacity:0;">
        Earn rewards fast 💰
    </div>

    <!-- FULL HEIGHT FIX (GMAIL BUG SOLUTION) -->
    <table role="presentation" width="100%" height="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="#0a192f">
        <tr>
            <td valign="top" style="vertical-align:top !important; padding:0; margin:0;">

                <!-- MAIN CONTAINER -->
                <table role="presentation" align="center" width="100%" cellpadding="0" cellspacing="0" border="0"
                       style="max-width:500px; background:#ffffff;">

                    <!-- HEADER -->
                    <tr>
                        <td style="background:#0a192f; text-align:center; padding:15px;">
                            <div style="font-size:22px;">🛍️</div>
                            <div style="color:#f97316; font-size:18px; font-weight:bold;">HeavyDeals</div>
                            <div style="color:#94a3b8; font-size:11px;">Earn Rewards for Reviews</div>
                        </td>
                    </tr>

                    <!-- WELCOME -->
                    <tr>
                        <td style="padding:15px;">
                            <div style="font-size:16px; font-weight:bold;">
                                Welcome, {buyer_name}! 🎉
                            </div>
                            <div style="font-size:13px; color:#64748b; margin-top:5px;">
                                Get ready to earn rewards!
                            </div>
                        </td>
                    </tr>

                    <!-- BONUS -->
                    <tr>
                        <td style="padding:0 15px 15px;">
                            <table width="100%" bgcolor="#ffedd5">
                                <tr>
                                    <td style="padding:10px; text-align:center;">
                                        <div style="font-size:12px; font-weight:bold;">✨ First Order Bonus</div>
                                        <div style="font-size:16px; color:#f97316; font-weight:bold;">
                                            UP TO ₹500 EXTRA
                                        </div>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>

                    <!-- STEPS -->
                    <tr>
                        <td style="padding:10px 15px;">
                            <div style="text-align:center; font-weight:bold; font-size:12px;">
                                ⚡ How It Works
                            </div>

                            <table width="100%" style="margin-top:10px;">
                                <tr>
                                    <td align="center">📦<br><span style="font-size:11px;">Order</span></td>
                                    <td align="center">⭐<br><span style="font-size:11px;">Review</span></td>
                                    <td align="center">💰<br><span style="font-size:11px;">Get Paid</span></td>
                                </tr>
                            </table>
                        </td>
                    </tr>

                    <!-- BENEFITS -->
                    <tr>
                        <td style="padding:0 15px 15px;">
                            <table width="100%" bgcolor="#f0fdf4">
                                <tr>
                                    <td style="padding:10px;">
                                        <div style="color:#16a34a; font-size:12px; font-weight:bold;">
                                            🎁 What You Get
                                        </div>
                                        <div style="font-size:11px;">✅ 50% refund on every review</div>
                                        <div style="font-size:11px;">✅ Bonus for first 5 orders</div>
                                        <div style="font-size:11px;">✅ Priority support</div>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>

                    <!-- BUTTON -->
                    <tr>
                        <td align="center" style="padding:15px;">
                            <a href="https://heavy-deal-a5in.onrender.com/buyer/dashboard"
                               style="background:#f97316; color:#fff; padding:10px 20px;
                                      text-decoration:none; border-radius:20px; font-size:13px;">
                                🚀 Start Earning
                            </a>
                        </td>
                    </tr>

                    <!-- FOOTER -->
                    <tr>
                        <td style="text-align:center; padding:10px; font-size:10px; color:#64748b;">
                            Need help? heavydeals567@gmail.com<br>
                            © HeavyDeals
                        </td>
                    </tr>

                </table>

            </td>
        </tr>
    </table>

    </body>
    </html>
    """

    return send_email(to_email, "Welcome to HeavyDeals 🎉", html_content, is_html=True)
    
def send_otp_email(to_email, name, otp):
    """
    Send OTP for email verification
    """
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Email Verification - HeavyDeals</title>
    </head>
    <body style="margin:0; padding:0; font-family: Arial, Helvetica, sans-serif; background:#f0f2f5;">
        <table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin:0; padding:20px 0;">
            <tr>
                <td align="center">
                    <table width="100%" cellpadding="0" cellspacing="0" border="0" style="max-width:480px; width:100%; background:#ffffff; border-radius:24px; overflow:hidden; box-shadow:0 10px 30px rgba(0,0,0,0.1);">
                        
                        <!-- Header -->
                        <tr>
                            <td bgcolor="#0a192f" style="background:#0a192f; padding:25px 20px; text-align:center;">
                                <img src="https://heavy-deal-a5in.onrender.com/static/logo.png" alt="HeavyDeals" style="width:60px; height:60px; border-radius:12px;">
                                <h1 style="color:#f97316; margin:10px 0 0; font-size:22px;">HeavyDeals</h1>
                                <p style="color:#94a3b8; margin:5px 0 0; font-size:12px;">Verify Your Email Address</p>
                            </td>
                        </tr>
                        
                        <!-- Body -->
                        <tr>
                            <td style="padding:30px 25px;">
                                <h2 style="color:#0a192f; margin:0 0 10px; font-size:18px;">Hello {name},</h2>
                                <p style="color:#64748b; margin:0 0 20px; font-size:14px; line-height:1.5;">
                                    Thank you for registering with HeavyDeals! Please use the verification code below to complete your registration.
                                </p>
                                
                                <!-- OTP Box -->
                                <table width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="#ffedd5" style="background:#ffedd5; border-radius:16px; margin:20px 0;">
                                    <tr><td style="padding:20px; text-align:center;">
                                        <p style="color:#64748b; margin:0 0 10px; font-size:12px;">Your Verification Code</p>
                                        <div style="background:#ffffff; padding:15px; border-radius:12px; display:inline-block;">
                                            <span style="font-size:32px; font-weight:800; letter-spacing:8px; color:#f97316;">{otp}</span>
                                        </div>
                                        <p style="color:#d97706; margin:15px 0 0; font-size:11px;">⏰ This code expires in 5 minutes</p>
                                    </td></tr>
                                </table>
                                
                                <p style="color:#64748b; margin:20px 0 0; font-size:13px; line-height:1.5;">
                                    If you didn't request this, please ignore this email.
                                </p>
                            </td>
                        </tr>
                        
                        <!-- Footer -->
                        <tr>
                            <td style="padding:20px; background:#f8fafc; text-align:center; border-top:1px solid #e2e8f0;">
                                <p style="color:#64748b; margin:0; font-size:11px;">Need help? Contact us at <a href="mailto:heavydeals567@gmail.com" style="color:#f97316;">heavydeals567@gmail.com</a></p>
                                <p style="color:#94a3b8; margin:10px 0 0; font-size:10px;">© 2024 HeavyDeals. All rights reserved.</p>
                            </td>
                        </tr>
                        
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
    return send_email(to_email, "Verify Your Email - HeavyDeals", html_content, is_html=True)
