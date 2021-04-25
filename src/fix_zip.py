import pandas as pd
import numpy as np
import logging


class fix_zip:
    def __init__(self, filepath):
        self.path = filepath

    def load_data(self, fname):
        try:
            d = pd.read_csv(self.path + fname)
        except Exception as e:
            logging.error('Failed loading data {}. {}'.format(fname, e))
            return False
        logging.info(self.path + fname + ' loaded successfully')
        return d

    def match(self):
        logging.info('Starting zip code mapping process...')
        zip_lkp = self.load_data('zip_lookup.csv')
        ccw = self.load_data('cities_crosswalk.csv')

        '''d = np.zeros([len(ccw), 6])
        d = pd.DataFrame(d)
        headers = ['Unique_City_ID', 'City', 'County', 'State_Abbr', 'Zip', 'State']
        d.columns = headers
        for i, col in d.items():
            d[i] = col.astype(object)

        out = []
        prev = 0
        for i, row in d.iterrows():
            percent = round((i/len(d)) * 100, 2)
            if percent % 10 == 0 and percent != prev:
                print(str(percent) + '% complete.')
                prev = percent

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
        out.to_csv(self.path + 'not_found.csv', index=False)'''
        logging.info('Mapping process complete')
        logging.info('8264 records with no matching zip code')
        self.fill_missing()

    def fill_missing(self):
        logging.info('Filling state abbreviations to unmapped zip codes')
        nf = self.load_data('not_found.csv')
        zip_lkp = self.load_data('zip_lookup.csv')
        ncw = self.load_data('new_cities_cw.csv')
        cw = self.load_data('cities_crosswalk.csv')
        '''for i, row in nf.iterrows():
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

        ncw.to_csv(self.path + 'new_cities_crosswalk.csv', index=False)'''
        logging.info('Full state name fill complete')

    def main(self):
        self.match()


if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s %(levelname)-4s %(message)s',
                        filename='fix_zip.log',
                        filemode='w',
                        level=logging.DEBUG,
                        datefmt='%Y-%m-%d %H:%M:%S')
    path = '../data/'
    fz = fix_zip(path)
    fz.main()


