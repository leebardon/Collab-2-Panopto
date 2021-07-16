import smtplib, ssl
import os
import csv
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from config.Config import credentials as config
from src.views import Logger

smtp_server = config["smtp_server"]
sender_email = config["sender_email"]
receiver_info_email = config["receiver_info_email"]
receiver_alert_email = config["receiver_alert_email"]

BASE = os.getcwd()
LOGGER = Logger.init_logger(__name__)


def create_email():
    message = MIMEMultipart("alternative")
    message["Subject"] = "Panopto is missing course folders"
    body = MIMEText(get_html(), "html", "utf-8")
    message.attach(body)
    return message


def get_html():
    email = f"{BASE}/data/email.html"
    HtmlFile = open(email, "r", encoding="utf-8")
    return HtmlFile.read()


def get_html_alert():
    email = f"{BASE}/data/email_alert.html"
    HtmlFile = open(email, "r", encoding="utf-8")
    return HtmlFile.read()


def send_info_email(message: MIMEMultipart):
    send_email(message, False)


def send_alert_email(message: MIMEMultipart):
    send_email(message, True)


def send_email(message: MIMEMultipart, alert=False):
    if alert == True:
        receiver_email = receiver_alert_email
    else:
        receiver_email = receiver_info_email

    message["From"] = sender_email
    message["To"] = receiver_alert_email

    # Create a secure SSL context
    context = ssl.create_default_context()

    with smtplib.SMTP(smtp_server) as server:
        server.ehlo()  # Can be omitted
        server.starttls(context=context)
        server.sendmail(sender_email, receiver_email, message.as_string())


def attach_missing_and_failed_csv(
    message: MIMEMultipart, missing_folders: list, failed_uploads: list
):
    csv_missing_folders = generate_csv(missing_folders, "missing_folders.csv")
    csv_failed_uploads = generate_csv(failed_uploads, "failed_uploads.csv")

    with open(csv_missing_folders, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header(
        "Content-Disposition", f"attachment; filename= {csv_missing_folders}",
    )
    message.attach(part)

    with open(csv_failed_uploads, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header(
        "Content-Disposition", f"attachment; filename= {csv_failed_uploads}",
    )
    message.attach(part)

    os.unlink(csv_missing_folders)
    os.unlink(csv_failed_uploads)

    return message


def generate_csv(missing_folders, fname):
    f = open(fname, "w", encoding="UTF8")
    writer = csv.writer(f, delimiter=",")

    for folder in missing_folders:
        writer.writerow([folder])
    f.close()

    return fname


def create_alert_message(trace_back: str):
    # Create message body
    message = MIMEMultipart("alternative")
    message["Subject"] = "Collab-2-Panopto encountered a serious problem"
    part1 = MIMEText(get_html_alert(), "html", "utf-8")
    message.attach(part1)

    # Create traceback file
    f = open("traceback.txt", "w")
    f.write(trace_back)
    f.close()

    # Attach traceback to message
    with open("traceback.txt", "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())

    encoders.encode_base64(part)
    part.add_header(
        "Content-Disposition", f"attachment; filename= traceback.txt",
    )
    message.attach(part)
    os.unlink("traceback.txt")

    # Attach log to message
    with open(f"{BASE}/.logs/info.log", "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())

    encoders.encode_base64(part)
    part.add_header(
        "Content-Disposition", f"attachment; filename= info.log",
    )
    message.attach(part)

    # Attach debug log to message
    with open(f"{BASE}/.logs/dbg.log", "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())

    encoders.encode_base64(part)
    part.add_header(
        "Content-Disposition", f"attachment; filename= dbg.log",
    )
    message.attach(part)

    # Return message
    return message
