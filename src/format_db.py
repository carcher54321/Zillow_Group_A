import cx_Oracle as orc
import os
import pandas as pd
import logging


def load_data(fname):
    return pd.read_csv('../data/' + fname)


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


def get_header_type(d):
    h_init = '('
    for i, col in d.items():
        # Oracle only allows column names less than 30 characters
        header = i
        if len(i) > 30:
            prefix = replace_header(i.split('_')[0])
            suffix = replace_header(i.split('_')[1])

            header = prefix + '_' + suffix
            if len(header) > 29:
                print(header + str(len(header)))

        # Date is a reserved word
        if header == 'Date':
            header = 'Date_Column'

        h_init += header + ' '
        h_init += 'VARCHAR2(50)'

        if i == d.columns[-1]:
            h_init += ')'
        else:
            h_init += ', '

    return h_init


def get_d_format(n):
    f = '('
    for i in range(n):
        f += ':' + str(i)
        if i == n - 1:
            f += ')'
        else:
            f += ', '
    return f


class Format_Db:
    def __init__(self):
        self.dsn = orc.makedsn('localhost', '1521', service_name='orcl')
        self.user = 'zillow_group_a'
        self.password = 'root'

    def create_table(self, fname):
        table_name = fname[:-4]
        data = load_data(fname)

        db = orc.connect(
            user=self.user,
            password=self.password,
            dsn=self.dsn
        )
        cursor = db.cursor()

        sql = "SELECT table_name FROM user_tables WHERE table_name = '" + table_name.upper() + "'"
        cursor.execute(sql)

        if cursor.fetchone():
            logging.info('Table {} already exists.'.format(table_name))
        else:
            headers = get_header_type(data)
            sql = 'CREATE TABLE ' + table_name + '' + headers
            try:
                cursor.execute(sql)
                logging.info('Table {} created.'.format(table_name))
            except Exception as e:
                logging.error('Failed creating table {}: {}'.format(table_name, e))

        cursor.close()
        db.close()
        self.insert_data(data, table_name)

    def insert_data(self, data, table_name):
        db = orc.connect(
            user=self.user,
            password=self.password,
            dsn=self.dsn
        )
        cursor = db.cursor()

        sql = 'SELECT * FROM ' + table_name
        cursor.execute(sql)
        if cursor.fetchone():
            logging.info('Table {} already contains data.'.format(table_name))
        else:
            format = get_d_format(len(data.columns))
            try:
                for i, row in data.iterrows():
                    row = row.fillna('NaN')
                    sql = 'INSERT INTO ' + table_name + ' VALUES ' + format
                    cursor.execute(sql, tuple(row))
                    db.commit()
                logging.info('Data written to table {}.'.format(table_name))
            except Exception as e:
                logging.error('Failed inserting data into table {}: {}'.format(table_name, e))

        cursor.close()
        db.close()

    def main(self):
        fnames = os.listdir('../data/')
        for n in fnames:
            self.create_table(n)


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s %(levelname)-4s %(message)s',
                        filename='../logs/format_db.log',
                        filemode='w',
                        level=logging.DEBUG,
                        datefmt='%Y-%m-%d %H:%M:%S')
    make_db = Format_Db()
    make_db.main()
