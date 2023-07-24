import os
import smtplib
from dotenv import load_dotenv
from email.message import EmailMessage


load_dotenv()

def send_email(subject, content, to_email, attachment_path=None):
    msg = EmailMessage()
    msg.set_content(content)
    msg['Subject'] = subject
    msg['From'] = "vnicoud@yahoo.fr"
    msg['To'] = to_email

    # Check for an attachment and attach if exists
    if attachment_path:
        with open(attachment_path, 'rb') as file:
            file_content = file.read()
            file_name = os.path.basename(attachment_path)
            msg.add_attachment(file_content, maintype='application', subtype='octet-stream', filename=file_name)


    EMAIL_HOST = os.getenv('EMAIL_HOST')
    EMAIL_PORT = os.getenv('EMAIL_PORT')
    EMAIL_USER = os.getenv('EMAIL_USER')
    EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')

    try:
        # Connexion au serveur SMTP et envoi de l'e-mail
        with smtplib.SMTP_SSL(EMAIL_HOST, EMAIL_PORT) as server:
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.send_message(msg)
        print("E-mail sent successfully!")
    except Exception as e:
        print(f"Failed to send email due to: {e}")

def main(subject, content, to_email):
    send_email(subject, content, to_email)

def run_smtp_transfer(subject, content, to_email):
    main(subject, content, to_email)