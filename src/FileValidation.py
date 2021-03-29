import os
import pandas as pd
import numpy as np
import logging



class FileValidation:
    
    def __init__(self,filepath):
        self.file = filepath
        self.error = None
        self.df = None
    def validate(self): #-> return True/False
        logging.info("Begining file validation")
        isempty = os.stat(self.file).st_size == 0 # checks if the file is empty

        if isempty :# empty check -> email if empty
            logging.error("The file is empty")
            self.error = "The File is Empty"
            B = False 
            return B
        else:
            logging.info("the file isnt not empty")
            self.df = pd.read_csv(self.file)
            A = self.type_check(self.df) # type check
            return  A # function must return true 

    def type_check(self,df):
        logging.info("Checking the data types of each columns")
        type_list=[]
        for column in df:
            type_list.append(df.dtypes[column])

        self.NAN_replacement(self.df) # NAN replacement
        
        col_num = 0 
        for col in df: #iterating over the columns

            for cell in df[col].values: #checking each cell 
                if type_list[col_num] == "int64":
                    if cell == "Nan" or type(cell) == np.int64 or type(cell) == int:
                        continue
                    else:
                        logging.error("The required data type: %s and cell data type %s"%(type_list[col_num],type(cell)))
                        self.error = "Invalid Data Types"
                        return False


                elif type_list [col_num] == "float64":
                    if cell == "Nan" or type(cell) == np.float64 or type(cell) == float:
                        continue
                    else:
                        
                        logging.error("The required data type: %s and cell data type %s"%(type_list[col_num],type(cell)))
                        self.error = "Invalid Data Types"
                        return False
                
                elif type_list[col_num] == "object":
                    if cell == "Nan" or type(cell) == str:
                        continue
                    else:
                        logging.error("The required data type: %s and cell data type %s"%(type_list[col_num],type(cell)))
                        self.error = "Invalid Data Types"
                        return False
                
                else:
                    logging.error("The required data type: %s and cell data type %s"%(type_list[col_num],type(cell)))
                    self.error = "Invalid Data Types"
            col_num+=1

        return True

    
    def get_errors(self):  #returns the error values
        return self.error

    def NAN_replacement(self,df): #replace null values with Nan
        logging.info("Replacing null values to Nan")
        df.fillna("Nan", inplace = True)
        return

    def save_to_csv(self,outputfile):
        if self.df != None:
            logging.info("saving the Dateframe to an outputfile")
            self.df.to_csv(outputfile,header=True)
        else:
            logging.error("The dataframe does not exist")
            
    def db_stage(self):
        # check/create table
        # check/create headers
        # input data
        return


# if __name__ == "__main__":
#     os.chdir(os.path.dirname(__file__))
#     validator = FileValidation("CountyCrossWalk_Zillow.csv")
#     print(validator.validate())
