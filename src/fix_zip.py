import pandas as pd
import numpy as np
import logging


class fix_zip:
    def __init__(self, filepath):
        self.path = filepath

    def match(self):
        logging.info('Starting matching process')
        zip_lkp = pd.read_csv(self.path + 'zip_lookup.csv', index_col=0)
        ccw = pd.read_csv(self.path + 'cities_crosswalk.csv')

        d = np.zeros([len(ccw), 7])
        d = pd.DataFrame(d)
        headers = ['Unique_City_ID', 'City', 'County', 'State_Abbr', 'Zip', 'State']
        d.columns = headers
        for i, col in d.items():
            d[i] = col.astype(object)

        out = []
        for i, row in d.iterrows():
            a = ccw.loc[i]
            found = False
            temp = zip_lkp[zip_lkp['city'].str.strip().str.upper() == a['City'].strip().upper()]
            for j, rowb in temp.iterrows():
                if a['County'].strip().upper() == rowb['county_name'].strip().upper():
                    if a['State'].strip().upper() == rowb['state_id'].strip().upper():
                        b = rowb[['zip', 'state_name']]
                        found = True
                        continue

            if found:
                r = pd.concat([a.reset_index(drop=True), b.reset_index(drop=True)], axis=0).reset_index(drop=True)
                r.index = ['Unique_City_ID', 'City', 'County', 'State_Abbr', 'Zip', 'State']
                d.loc[i] = r
            else:
                out.append(a)

        d.to_csv(self.path + 'new_cities_cw.csv', index=False)
        out = pd.DataFrame(out)
        out.to_csv(self.path + 'not_found.csv', index=False)
        logging.info('Mapping process complete')
        self.fill_missing()

    def fill_missing(self):
        logging.info('Filling state abbreviations to unmapped zip codes')
        nf = pd.read_csv(self.path + 'not_found.csv')
        zip_lkp = pd.read_csv(self.path + 'new_zip_lkp.csv', index_col=0)
        ncw = pd.read_csv(self.path + 'new_cities_cw.csv')
        cw = pd.read_csv(self.path + 'cities_crosswalk.csv')
        for i, row in nf.iterrows():
            print(i)
            temp = zip_lkp[zip_lkp['state_id'].str.strip().str.upper() == row['State'].strip().upper()]
            temp = temp[temp['county_name'].str.strip().str.upper() == row['County'].strip().upper()]

            city_id = cw.loc[i]['Unique_City_ID']
            city = cw.loc[i]['City']
            county = cw.loc[i]['County']
            state_abbr = cw.loc[i]['State']
            zip_code = np.nan

            if temp.empty:
                temp = zip_lkp[zip_lkp['state_id'].str.strip().str.upper() == row['State'].strip().upper()]
                state = temp.iloc[0]['state_name']

            r = pd.Series([city_id, city, county, state_abbr, zip_code, state])
            r.index = ['Unique_City_ID', 'City', 'County', 'State_Abbr', 'Zip', 'State']
            ncw.loc[i] = r

        ncw.to_csv(self.path + 'new_cities_crosswalk.csv', index=False)
        logging.info('State abbreviation fill complete')

    def main(self):
        self.match()


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s %(levelname)-4s %(message)s',
                        filename='../logs/format_db.log',
                        filemode='w',
                        level=logging.DEBUG,
                        datefmt='%Y-%m-%d %H:%M:%S')
    path = '../data/'
    fz = fix_zip(path)
    fz.main()


