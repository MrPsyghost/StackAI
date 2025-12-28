import smtplib
from email.message import EmailMessage

EMAIL_ADDRESS = "psyghostgames@gmail.com"
EMAIL_PASSWORD = "nncu jtph uies xinu"

def Email(to, subject, content, html=None):
    msg = EmailMessage()
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to
    msg["Subject"] = subject

    msg.set_content(content)
    if html:
        msg.add_alternative(html, subtype="html")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
