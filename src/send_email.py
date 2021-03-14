import yagmail

def sendEmail():
    logging.info("Sending an email")

    receiver = "your_email@gmail.com" #receiver
    body = "This is the log file"
    
    log = "logFile.log"  
    graph = 'graph1.png'

    yag = yagmail.SMTP("your_email@gmail.com") #sender
    
    yag.send(
        to=receiver,
        subject="Log File",
        contents=body, 
        attachments=[log,graph]
    )
