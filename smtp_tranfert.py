import smtplib
from email.message import EmailMessage

def send_email(subject, content, to_email):
    msg = EmailMessage()
    msg.set_content(content)
    msg['Subject'] = subject
    msg['From'] = "your_email@example.com"
    msg['To'] = to_email

    # Connexion au serveur SMTP et envoi de l'e-mail
    with smtplib.SMTP_SSL('smtp.example.com', 465) as server:
        server.login("your_email@example.com", "your_password")
        server.send_message(msg)
