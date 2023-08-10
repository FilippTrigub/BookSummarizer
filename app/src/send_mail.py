import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders

from src.GlobalLogger import log_info
from src.email_text import email_text


def send_mail(recipient_email, subject, attachment_paths, book_title):
    # Set up the SMTP server
    smtp_server = 'smtp.dreamhost.com'
    port = 465  # For ssl
    sender_email = "filipp@trigub.tech"
    password = "E5M#z&Sczf7kerHy" # "Mf@ttA6GqtmK9&zn"

    # Create a multipart message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject

    # Add your message body
    log_info(os.getcwd())
    log_info(os.listdir())
    msg.attach(MIMEText(email_text, 'utf-8'))

    # Open the file in binary mode
    for path in attachment_paths:
        with open(path, "rb") as attachment:
            part = MIMEBase("application", "vnd.openxmlformats-officedocument.wordprocessingml.document")
            part.set_payload(attachment.read())

        # Encode to base64
        encoders.encode_base64(part)

        # Add header
        if 'book_summary' in path:
            filename = f'Book summary of {book_title}.docx'
        elif 'chapter_summary' in path:
            filename = f'Chapter summary of {book_title}.docx'
        else:
            filename = f'Summary of {book_title}.docx'
        part.add_header("Content-Disposition", f"attachment; filename={filename}")

        # Add attachment to message
        msg.attach(part)

    # Use the SMTP server to send the email
    server = smtplib.SMTP_SSL(smtp_server, port)
    server.login(sender_email, password)
    text = msg.as_string()
    server.sendmail(sender_email, recipient_email, text)
    server.quit()
    log_info("Mail sent!")


if __name__ == "__main__":
    send_mail('filipp.trigub@gmail.com', 'bar', os.path.join('../book_summaries', '2023_06_22_21_28_03_test'), 'test')
