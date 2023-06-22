import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders


def send_mail(recipient, subject, file_path, book_name):
    # Set up the SMTP server
    smtp_server = 'smtp.office365.com'
    port = 587  # For starttls
    sender_email = "info@librevita.com"
    password = "cRgq@@hJf7NJR@nF"

    # Create a multipart message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient
    msg['Subject'] = subject

    # Add your message body
    msg.attach(MIMEText("body", 'plain'))

    # Open the file in binary mode
    with open(file_path, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())

    # Encode to base64
    encoders.encode_base64(part)

    # Add header
    part.add_header("Content-Disposition", f"attachment; filename=Summary of {book_name}.txt")

    # Add attachment to message
    msg.attach(part)

    # Use the SMTP server to send the email
    server = smtplib.SMTP(smtp_server, port)
    server.starttls()
    server.login(sender_email, password)
    text = msg.as_string()
    server.sendmail(sender_email, recipient, text)
    server.quit()
    print("Mail sent!")


if __name__ == "__main__":
    send_mail('filipp.trigub@gmail.com', 'bar', os.path.join('book_summaries', '2023_06_22_21_28_03_test'), 'test')
