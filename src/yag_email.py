import yagmail
import keyring

RECIPIENTS = []

def set_password(email, password):
    global FROM_ADDRESS
    FROM_ADDRESS = email
    yagmail.register(email, password) # registering the email
    # is this next line necessary? docs seem like that's not the case
    keyring.set_password('yagmail', email, password)  #setting the password

def sendEmail(sender, subject, body, receiver, attachments):
    logging.info("Sending an email")
    RECIPIENTS.append(receiver)

    yag = yagmail.SMTP(sender) #sender
    for recipient in RECIPIENTS:
        yag.send(
            to=recipient,
            subject=subject,
            contents=body, 
            attachments=attachments
        )
