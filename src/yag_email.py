import yagmail
import keyring

FROM_ADDRESS = 'your_email@gmail.com'
RECIPIENTS = ['to_email@gmail.com']

def set_password(email, password):
    global FROM_ADDRESS
    FROM_ADDRESS = email
    yagmail.register('@gmail.com', password) # registering the email
    keyring.set_password('yagmail', email, password)  #setting the password

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
