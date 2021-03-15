import os
import yagmail
import pandas as pd
import mysql.connector



class FileValidation:
    ##import Database
    def __init__(self,filepath):
        self.file = filepath
        

    def validate(self): #-> return True/False

        isempty = os.stat(self.file).st_size == 0 # checks if the file is empty

        if isempty :# empty check -> email if empty
            B = self.emptyfile() 
            return B
        else:
            self.df = pd.read_csv(self.file)
            A = self.type_check(self.df) # type check
            
            C = self.NAN_replacement(self.df) # NAN replacement

            return  A and C # both the functions must return true 

    def type_check(self,df):

        # for index, row in df.iterrows():
        #     continue

        return True

    def emptyfile(self): #email if empty
       
        def sendEmail():
            # logging.info("Sending an email")

            receiver = "adamx083@gmail.com" #receiver
            body = "This File is empty"

            empty_file = self.file

            yag = yagmail.SMTP("adamx083@gmail.com") #sender
            
            yag.send(
                to=receiver,
                subject="Empty File",
                contents=body, 
                attachments= empty_file
            )
            
        sendEmail()
        return False
        

    def NAN_replacement(self,df): #replace null values with Nan
        df.fillna("Nan")
        return True


    def db_stage(self):
        return 
        # connect to database
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="root",
            database= "zillow_group_a"
        ) 

        # get cursor object 
        cursor = db.cursor() 
  
        # execute your query 
        cursor.execute("SELECT * FROM County_time_series") 
        
        # fetch all the matching rows 
        result = cursor.fetchall() 
        
        # loop through the rows 
        # for row in result: 
        #     print(row, '\n') 




        # check/create table
        # check/create headers
        # input data


# if __name__ == "__main__":
#     os.chdir(os.path.dirname(__file__))
#     validator = FileValidation("u.data")
#     print(validator.validate())