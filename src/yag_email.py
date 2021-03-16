import yagmail
import keyring
import logging

RECIPIENTS = []


def set_password(email, password):
    yagmail.register(email, password)  # registering the email
    # is this next line necessary? docs seem like that's not the case
    keyring.set_password('yagmail', email, password)  # setting the password


def sendEmail(sender, subject, body, recipients, attachments):
    logging.info("Sending an email")
    if type(recipients) is str:
        RECIPIENTS.append(recipients)
    else:
        for r in recipients:
            RECIPIENTS.append(r)

    yag = yagmail.SMTP(sender)  # sender
    for recipient in RECIPIENTS:
        yag.send(
            to=recipient,
            subject=subject,
            contents=body,
            attachments=attachments
        )
