import os
import smtplib
from dotenv import load_dotenv
from email.message import EmailMessage


load_dotenv()
WARNING_COLOR = os.getenv("WARNING_COLOR").encode().decode('unicode_escape')
OK_COLOR = os.getenv("OK_COLOR").encode().decode('unicode_escape')
ERROR_COLOR = os.getenv("ERROR_COLOR").encode().decode('unicode_escape')
RESET_COLOR = os.getenv("RESET_COLOR").encode().decode('unicode_escape')

def time_from_env(key):
    """Convertit une chaîne HH:MM depuis .env en un objet time."""
    hours, minutes = map(int, os.getenv(key).split(":"))
    return time(hours, minutes)

def should_send_email():
    current_time = datetime.now().time()  # Obtient l'heure actuelle
    
    # Récupérer les heures de début et de fin depuis le fichier .env
    morning_start = time_from_env('MORNING_START')
    morning_end = time_from_env('MORNING_END')
    evening_start = time_from_env('EVENING_START')
    evening_end = time_from_env('EVENING_END')

    # Vérifier si l'heure actuelle se situe dans une des plages horaires
    return morning_start <= current_time <= morning_end or evening_start <= current_time <= evening_end

def send_email(subject, content, to_email, attachment_path):
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
        print(OK_COLOR + "E-mail sent successfully!" + RESET_COLOR)
    except Exception as e:
        print(ERROR_COLOR + f"Failed to send email due to: {e}" + RESET_COLOR)

def main(subject, content, to_email, attachment_path):
    send_email(subject, content, to_email, attachment_path)

def run_smtp_transfer(subject, content, to_email, attachment_path):
    main(subject, content, to_email, attachment_path)