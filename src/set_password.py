import yagmail
import keyring

yagmail.register('@gmail.com', 'your_password') # registering the email
keyring.set_password('yagmail', 'your_email@gmail.com', 'your_password')  #setting the password
