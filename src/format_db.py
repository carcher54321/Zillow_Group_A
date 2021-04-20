import cx_Oracle as orc
import pandas as pd
import logging
import config
from fix_zip import fix_zip
import gmail_connect


def replace_header(h):
    header_map = {'InventorySeasonallyAdjusted': 'InvSeasAdj',
                  'MedianListingPricePerSqft': 'MedLstPrPerSqft',
                  'MedianListingPrice': 'MedLstPr',
                  'MedianPctOfPriceReduction': 'MedPctOfPrRed',
                  'MedianRentalPricePerSqft': 'MedRntPrPerSqft',
                  'MedianRentalPrice': 'MedRntPr',
                  'PctOfHomesDecreasingInValues': 'PctOfHomeDecVal',
                  'PctOfHomesIncreasingInValues': 'PctOfHomeIncVal',
                  'PctOfListingsWithPriceReductionsSeasAdj': 'PctLstPrRedSeasAdj',
                  'SingleFamilyResidence': 'SnglFamRes',
                  'MultiFamilyResidence5PlusUnits': 'MltFmRes5Uts',
                  'MedianPriceCutDollar': 'MedPrCutDlr',
                  'PctOfHomesSellingForGain': 'PctOfHmsSlngGain',
                  'PctOfHomesSellingForLoss': 'PctOfHmsSlngLoss',
                  'PctOfListingsWithPriceReductions': 'PctOfLstsWitPrRed',
                  'SingleFamilyResidenceRental': 'SnglFamResRent',
                  '5BedroomOrMore': '5BedOrMore'}

    if h in header_map.keys():
        return header_map[h]

    return h


def get_header_type(d, fname, s):
    h_init = '('
    for i, col in d.items():
        # Oracle only allows column names less than 30 characters
        header = i
        if len(i) > 30:
            prefix = replace_header(i.split('_')[0])
            suffix = replace_header(i.split('_')[1])

            header = prefix + '_' + suffix

        # Date is a reserved word
        if header == 'Date':
            header = 'Date_Column'

        if not s:
            if fname not in ['Cities_crosswalk.csv', 'CountyCrossWalk_Zillow.csv']:
                h_init += header + '1 '
                if header == 'Date_Column':
                    h_init += 'DATE'
                elif header == 'RegionName':
                    if fname in ['City_time_series.csv', 'State_time_series.csv']:
                        h_init += 'VARCHAR2(50)'
                    else:
                        h_init += 'NUMBER'
                else:
                    h_init += 'NUMBER'
            else:
                h_init += header + ' '
                if header in ['Zip', 'StateFIPS', 'CountyFIPS', 'CountyRegionID_Zillow',
                              'MetroRegionID_Zillow', 'FIPS', 'CBSACode']:
                    h_init += 'NUMBER(10)'
                else:
                    h_init += 'VARCHAR2(50)'
        else:
            h_init += 'VARCHAR2(50)'

        if i == d.columns[-1]:
            h_init += ')'
        else:
            h_init += ', '

    return h_init


class Format_Db:
    def __init__(self, path):
        self.dsn = orc.makedsn(config.DB_HOST, config.DB_PORT, service_name=config.DB_SERVICE)
        self.user = config.DB_USER
        self.password = config.DB_PASS
        self.path = path

    def load_data(self, fname):
        try:
            d = pd.read_csv(self.path + fname)
        except Exception as e:
            logging.error('Failed loading data {}. {}'.format(fname, e))
            return False
        return d

    def create_table(self, fname, staging):
        data = self.load_data(fname)
        if not type(data) == bool:
            table_name = fname[:-4]
            if staging:
                table_name = 'S_' + table_name.upper()
            else:
                table_name = 'T_' + table_name.upper()

            try:
                db = orc.connect(
                    user=self.user,
                    password=self.password,
                    dsn=self.dsn
                )
                cursor = db.cursor()
            except Exception as e:
                logging.error('Failed connecting to database, error: {}'.format(e))
            else:
                sql = "SELECT table_name FROM user_tables WHERE table_name = '" + table_name + "'"
                cursor.execute(sql)

                if cursor.fetchone():
                    logging.info('Table {} already exists.'.format(table_name))
                else:
                    headers = get_header_type(data, fname, staging)
                    sql = 'CREATE TABLE ' + table_name + '' + headers
                    try:
                        cursor.execute(sql)
                        logging.info('Table {} created.'.format(table_name))
                    except Exception as e:
                        logging.error('Failed creating table {}: {}'.format(table_name, e))

                cursor.close()
                db.close()

    def create_user(self, user):
        try:
            db = orc.connect(
                user=self.user,
                password=self.password,
                dsn=self.dsn
            )
            cursor = db.cursor()
        except Exception as e:
            logging.error('Failed connecting to database, error: {}'.format(e))
        else:
            logging.info('Creating user: {}'.format(user))
            sql1 = '''
            CREATE USER {} IDENTIFIED BY root
            DEFAULT TABLESPACE "ts_usr"
            TEMPORARY TABLESPACE TEMP'''.format(user)
            cursor.execute(sql1)
            sql2 = 'ALTER USER {} QUOTA UNLIMITED ON "ts_usr"'.format(user)
            cursor.execute(sql2)
            sql3 = 'GRANT "CONNECT" TO ' + user
            cursor.execute(sql3)
            sql4 = 'GRANT "RESOURCE" TO ' + user
            cursor.execute(sql4)
            sql5 = 'GRANT CREATE VIEW TO ' + user
            cursor.execute(sql5)
            logging.info('User creation complete')

    def send_email(self):
        gmail_connect.sendEmail(config.DB_EMAIL_SENDER, 'Preprocessing log', '', config.EMAIL_RECIPIENTS,
                                ['preprocessing.log'])

    def main(self):
        for s in [True, False]:
            for n in config.FILE_NAMES:
                self.create_table(n, s)
        fix = fix_zip(self.path)
        fix.main()
        self.send_email()


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s %(levelname)-4s %(message)s',
                        filename='preprocessing.log',
                        filemode='w',
                        level=logging.DEBUG,
                        datefmt='%Y-%m-%d %H:%M:%S')
    path = '../data/'
    make_db = Format_Db(path)
    make_db.main()
