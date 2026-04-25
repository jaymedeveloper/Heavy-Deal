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
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Welcome to HeavyDeals</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                margin: 0;
                padding: 0;
                background-color: #f0f2f5;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                background: #ffffff;
                border-radius: 24px;
                overflow: hidden;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
            }}
            .header {{
                background: linear-gradient(135deg, #0a192f 0%, #112240 100%);
                padding: 40px 30px;
                text-align: center;
            }}
            .logo {{
                width: 80px;
                height: 80px;
                background: #f97316;
                border-radius: 20px;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                margin-bottom: 20px;
            }}
            .logo span {{
                font-size: 48px;
            }}
            .header h1 {{
                color: #f97316;
                margin: 0;
                font-size: 28px;
                font-weight: 800;
                letter-spacing: -0.5px;
            }}
            .header p {{
                color: #94a3b8;
                margin: 10px 0 0;
                font-size: 14px;
            }}
            .content {{
                padding: 40px 35px;
            }}
            .greeting {{
                margin-bottom: 25px;
            }}
            .greeting h2 {{
                color: #0a192f;
                font-size: 24px;
                font-weight: 700;
                margin-bottom: 10px;
            }}
            .greeting p {{
                color: #64748b;
                font-size: 16px;
                line-height: 1.5;
            }}
            .highlight {{
                background: linear-gradient(135deg, #ffedd5, #fef3c7);
                border-radius: 16px;
                padding: 25px;
                margin: 25px 0;
                text-align: center;
                border: 1px solid #fed7aa;
            }}
            .highlight-text {{
                font-size: 18px;
                font-weight: 600;
                color: #0a192f;
                margin-bottom: 10px;
            }}
            .highlight-amount {{
                font-size: 32px;
                font-weight: 800;
                color: #f97316;
            }}
            .steps {{
                display: flex;
                justify-content: space-between;
                margin: 35px 0;
                gap: 15px;
            }}
            .step {{
                text-align: center;
                flex: 1;
                background: #f8fafc;
                padding: 20px 15px;
                border-radius: 16px;
                transition: transform 0.2s;
            }}
            .step:hover {{
                transform: translateY(-5px);
            }}
            .step-icon {{
                width: 50px;
                height: 50px;
                background: #f97316;
                border-radius: 50%;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                margin-bottom: 15px;
                font-size: 24px;
            }}
            .step-number {{
                background: #f97316;
                width: 28px;
                height: 28px;
                border-radius: 50%;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                margin-bottom: 10px;
                color: white;
                font-weight: bold;
                font-size: 14px;
            }}
            .step strong {{
                display: block;
                color: #0a192f;
                font-size: 16px;
                margin-bottom: 5px;
            }}
            .step small {{
                color: #64748b;
                font-size: 12px;
            }}
            .benefits {{
                background: #f0fdf4;
                border-radius: 16px;
                padding: 20px;
                margin: 25px 0;
                border-left: 4px solid #16a34a;
            }}
            .benefits h4 {{
                color: #16a34a;
                font-size: 16px;
                margin-bottom: 10px;
            }}
            .benefits ul {{
                list-style: none;
                padding: 0;
            }}
            .benefits li {{
                padding: 8px 0;
                color: #334155;
                display: flex;
                align-items: center;
                gap: 10px;
            }}
            .benefits li:before {{
                content: "✓";
                color: #16a34a;
                font-weight: bold;
                font-size: 18px;
            }}
            .button {{
                display: inline-block;
                background: linear-gradient(135deg, #f97316, #ea580c);
                color: white;
                padding: 14px 32px;
                text-decoration: none;
                border-radius: 50px;
                font-weight: 600;
                font-size: 16px;
                margin: 20px 0;
                transition: all 0.3s;
                box-shadow: 0 4px 15px rgba(249, 115, 22, 0.3);
            }}
            .button:hover {{
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(249, 115, 22, 0.4);
            }}
            .divider {{
                height: 1px;
                background: linear-gradient(90deg, transparent, #e2e8f0, transparent);
                margin: 25px 0;
            }}
            .social-links {{
                text-align: center;
                margin: 20px 0;
            }}
            .social-links a {{
                color: #64748b;
                text-decoration: none;
                margin: 0 10px;
                font-size: 20px;
            }}
            .footer {{
                background: #f8fafc;
                padding: 30px;
                text-align: center;
                border-top: 1px solid #e2e8f0;
            }}
            .footer p {{
                color: #64748b;
                font-size: 12px;
                margin: 5px 0;
            }}
            .footer a {{
                color: #f97316;
                text-decoration: none;
            }}
            @media (max-width: 480px) {{
                .container {{
                    border-radius: 0;
                }}
                .content {{
                    padding: 25px 20px;
                }}
                .steps {{
                    flex-direction: column;
                    gap: 12px;
                }}
                .step {{
                    display: flex;
                    align-items: center;
                    text-align: left;
                    gap: 15px;
                    padding: 15px;
                }}
                .step-icon {{
                    margin-bottom: 0;
                }}
                .step-number {{
                    width: 24px;
                    height: 24px;
                    font-size: 12px;
                }}
                .header {{
                    padding: 30px 20px;
                }}
                .highlight-amount {{
                    font-size: 28px;
                }}
            }}
        </style>
    </head>
    <body>
        <div style="padding: 20px;">
            <div class="container">
                <!-- Header -->
                <div class="header">
                    <div class="logo">
                        <span>🛍️</span>
                    </div>
                    <h1>HeavyDeals</h1>
                    <p>India's Trusted Review Mediation Platform</p>
                </div>
                
                <!-- Content -->
                <div class="content">
                    <div class="greeting">
                        <h2>Welcome, {buyer_name}! 🎉</h2>
                        <p>We're thrilled to have you on board. Get ready to earn rewards for your honest reviews!</p>
                    </div>
                    
                    <div class="highlight">
                        <div class="highlight-text">✨ Your First Order Bonus</div>
                        <div class="highlight-amount">Up to ₹500 Extra</div>
                        <p style="margin-top: 10px; font-size: 14px; color: #64748b;">Complete your first order today and get bonus rewards</p>
                    </div>
                    
                    <!-- How It Works -->
                    <h3 style="color: #0a192f; margin-bottom: 20px; text-align: center;">⚡ How It Works</h3>
                    <div class="steps">
                        <div class="step">
                            <div class="step-icon">📦</div>
                            <strong>Step 1</strong>
                            <small>Order product on Amazon</small>
                        </div>
                        <div class="step">
                            <div class="step-icon">⭐</div>
                            <strong>Step 2</strong>
                            <small>Submit review & screenshots</small>
                        </div>
                        <div class="step">
                            <div class="step-icon">💰</div>
                            <strong>Step 3</strong>
                            <small>Get paid via UPI</small>
                        </div>
                    </div>
                    
                    <!-- Benefits -->
                    <div class="benefits">
                        <h4>🎁 What You Get</h4>
                        <ul>
                            <li>50% refund on every successful review</li>
                            <li>Bonus rewards for first 5 orders</li>
                            <li>Priority support for active reviewers</li>
                            <li>Early access to new products</li>
                        </ul>
                    </div>
                    
                    <div class="divider"></div>
                    
                    <!-- Quick Tips -->
                    <div style="background: #fef3c7; border-radius: 12px; padding: 15px; margin: 20px 0;">
                        <p style="color: #d97706; font-size: 14px; margin: 0;">
                            <strong>💡 Pro Tip:</strong> Submit high-quality screenshots and detailed reviews for faster approval!
                        </p>
                    </div>
                    
                    <!-- CTA Button -->
                    <div style="text-align: center;">
                        <a href="https://heavy-deal-a5in.onrender.com/buyer/dashboard" class="button">
                            🚀 Explore Products & Earn
                        </a>
                    </div>
                    
                    <div class="divider"></div>
                    
                    <!-- Contact Support -->
                    <div style="text-align: center; font-size: 13px; color: #64748b;">
                        <p>📧 Need help? Contact us at <a href="mailto:heavydeals567@gmail.com" style="color: #f97316;">heavydeals567@gmail.com</a></p>
                    </div>
                </div>
                
                <!-- Footer -->
                <div class="footer">
                    <div class="social-links">
                        <a href="#" style="margin: 0 8px;">📱</a>
                        <a href="#" style="margin: 0 8px;">🐦</a>
                        <a href="#" style="margin: 0 8px;">📘</a>
                        <a href="#" style="margin: 0 8px;">📷</a>
                    </div>
                    <p>© 2024 HeavyDeals - Earn Rewards for Honest Reviews</p>
                    <p>This is an automated message, please do not reply directly.</p>
                    <p><a href="https://heavy-deal-a5in.onrender.com">Visit Website</a> | <a href="#">Unsubscribe</a></p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    return send_email(to_email, f"Welcome to HeavyDeals! 🎉 Start Earning Rewards Today", html_content, is_html=True)
