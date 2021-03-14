import yagmail

FROM_ADDRESS = 'your_email@gmail.com'
RECIPIENTS = ['to_email@gmail.com']

def sendEmail(subject, body, receiver, attachments):
    logging.info("Sending an email")

    yag = yagmail.SMTP(FROM_ADDRESS) #sender
    for recipient in RECIPIENTS:
        yag.send(
            to=recipient,
            subject=subject,
            contents=body, 
            attachments=attachments
        )
