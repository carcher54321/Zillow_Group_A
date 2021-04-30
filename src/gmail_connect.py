import keyring
import smtplib
import ssl

from email.mime.base import MIMEBase
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

RECIPIENTS = []


def set_password(email, password):
    keyring.set_password('gmail', email, password)  # setting the password


def has_password(address):
    try:
        keyring.get_password('gmail', address)
    except Exception:
        return False
    else:
        return True


def prompt_password():
    em = input('enter the email address to add to the keychain: ')
    pw = input('enter that email\'s password: ')
    keyring.set_password('gmail', em, pw)


def sendEmail(sender, subject, body, recipients, attachments):
    def get_password():
        try:
            return keyring.get_password('gmail', sender)
        except Exception:
            raise SystemError(f'No password saved for email {sender}')
    if type(recipients) is str:
        RECIPIENTS.append(recipients)
    else:
        for r in recipients:
            RECIPIENTS.append(r)

    # SMTP port
    port = 465

    # class for holding all data for the email
    message = MIMEMultipart()
    # add headers
    message['From'] = sender
    message['Subject'] = subject
    # attach body
    message.attach(MIMEText(body, 'plain'))
    # read and attach all files
    for file_name in attachments:
        # read in bytes mode to handle all file types
        with open(file_name, 'rb') as attachment:
            part = MIMEBase('application', 'octet-stream')
            # add the file data to the MIME part
            part.set_payload(attachment.read())
        # apparently, encoding in ASCII is necessary for it to be in email
        encoders.encode_base64(part)
        # necessary headers to recognize as file attachment
        part.add_header("Content-Disposition", f'attachment; filename= {file_name}')
        # attach the file
        message.attach(part)
    # convert the message with attachments in order to send
    text = message.as_string()
    context = ssl.create_default_context()
    # connect to the gmail SMTP server
    with smtplib.SMTP_SSL('smtp.gmail.com', port, context=context) as server:
        # login to gmail account
        server.login(sender, get_password())
        # send email to each recipient
        for recipient in RECIPIENTS:
            server.sendmail(sender, recipient, text)


if __name__ == '__main__':
    prompt_password()
