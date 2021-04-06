import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sea
import datetime


S_FIPS_MAP = {
    'MS': 28, 'WV': 54, 'MI': 26, 'AL': 1, 'NM': 35, 'OK': 40, 'VT': 50, 'TN': 47, 'RI': 44, 'WI': 55, 'NY': 36,
    'DC': 11, 'CT': 9, 'NE': 31, 'WY': 56, 'VA': 51, 'MD': 24, 'HI': 15, 'MT': 30, 'ID': 16, 'KY': 21, 'KS': 20,
    'LA': 22, 'AK': 2, 'CO': 8, 'PA': 42, 'OR': 41, 'NC': 37, 'IN': 18, 'MO': 29, 'AR': 5, 'ME': 23, 'NH': 33, 'CA': 6,
    'OH': 39, 'MA': 25, 'NJ': 34, 'IL': 17, 'SD': 46, 'SC': 45, 'TX': 48, 'AZ': 4, 'UT': 49, 'WA': 53, 'FL': 12,
    'NV': 32, 'DE': 10, 'GA': 13, 'MN': 27, 'IA': 19, 'ND': 38
}
S_NAME_MAP = {
    'NM': 'NEWMEXICO', 'OK': 'OKLAHOMA', "WV": 'WESTVIRGINIA', 'AL': 'ALABAMA', 'MI': 'MICHIGAN', 'MS': 'MISSISSIPPI',
    'VT': 'VERMONT', 'NY': 'NEWYORK', 'RI': 'RHODEISLAND', 'TN': 'TENNESSEE', 'WI': 'WISCONSIN', 'CT': 'CONNECTICUT',
    'NE': 'NEBRASKA', 'WY': 'WYOMING', 'DC': 'DISTRICTOFCOLUMBIA', 'VA': 'VIRGINIA', 'HI': 'HAWAII', 'ID': 'IDAHO',
    'MD': 'MARYLAND', 'MT': 'MONTANA', 'KS': 'KANSAS', 'KY': 'KENTUCKY', 'LA': 'LOUISIANA', 'AK': 'ALASKA',
    'NH': 'NEWHAMPSHIRE', 'NC': 'NORTHCAROLINA', 'OR': 'OREGON', 'PA': 'PENNSYLVANIA', 'AR': 'ARKANSAS',
    'CO': 'COLORADO', 'IN': 'INDIANA', 'ME': 'MAINE', 'MO': 'MISSOURI', 'NJ': 'NEWJERSEY', 'OH': 'OHIO',
    'CA': 'CALIFORNIA', 'IL': 'ILLINOIS', 'MA': 'MASSACHUSETTS', 'SD': 'SOUTHDAKOTA', 'SC': 'SOUTHCAROLINA',
    'TX': 'TEXAS', 'UT': 'UTAH', 'AZ': 'ARIZONA', 'NV': 'NEVADA', 'WA': 'WASHINGTON', 'DE': 'DELAWARE', 'FL': 'FLORIDA',
    'GA': 'GEORGIA', 'IA': 'IOWA', 'MN': 'MINNESOTA', 'ND': 'NORTHDAKOTA'

}


class FileHelper:

    def __init__(self):
        self.STATE = self.data_path('vis_State_time_series.csv')
        self.CITY = self.data_path('vis_City_time_series.csv')
        self.METRO = self.data_path('vis_Metro_time_series.csv')
        self.NEIGHBORHOOD = self.data_path('vis_Neighborhood_time_series.csv')
        self.ZIP = self.data_path('vis_Zip_time_series.csv')
        self.COUNTY = self.data_path('vis_County_time_series.csv')
        self.COUNTY_CW = self.data_path('vis_COUNTYCROSSWALK_ZILLOW.csv')
        self.CITY_CW = self.data_path('vis_CITIES_CROSSWALK.csv')

    def data_path(self, relative):
        return os.path.join(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data'), relative)

    def fig_path(self, relative):
        return os.path.join(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'figures'), relative)


file_helper = FileHelper()
city_cw_df = pd.read_csv(file_helper.CITY_CW)
county_cw_df = pd.read_csv(file_helper.COUNTY_CW)


def pretty_print(lis, per_line):
    i = 0
    ln = len(lis)
    while i + per_line < ln:
        print(*lis[i:i+per_line], sep=', ')
        i += per_line
    if i < ln - 1:
        print(*lis[i:])


def get_region_data(filename, region):
    df = pd.read_csv(filename)
    data = df[df['REGIONNAME1'] == region]
    return data


def county_get_fips(county, st):
    data = county_cw_df[(county_cw_df['COUNTYNAME'] == county) & (county_cw_df['STATEFIPS'] == S_FIPS_MAP[st])]
    return list(data['FIPS'])[0]


def city_get_id(city, st):
    data = city_cw_df[(city_cw_df['CITY'] == city) & (city_cw_df['STATE_ABBR'] == st)]
    return list(data['UNIQUE_CITY_ID'])[0]


def city_get_county(city, st):
    data = city_cw_df[(city_cw_df['CITY'] == city) & (city_cw_df['STATE_ABBR'] == st)]
    return list(data['COUNTY'])[0]


def state_get_counties(st):
    data = county_cw_df[county_cw_df['STATEFIPS'] == S_FIPS_MAP[st]]
    return list(data['COUNTYNAME'])


def state_get_cities(st):
    data = city_cw_df[city_cw_df['STATE_ABBR'] == st]
    return list(data['CITY'])


def state_get_zips(st):
    data = city_cw_df[(city_cw_df['STATE_ABBR'] == st) & (city_cw_df['ZIP'].notnull())]
    return list(data['ZIP'])


def filter_level_data(level, enclosing, enclosed):
    if level == 'zip/state':
        regions = enclosed
        filename = file_helper.ZIP
    elif level == 'city/state':
        regions = [city_get_id(cit, enclosing) for cit in enclosed]
        filename = file_helper.CITY
    elif level == 'county/state':
        regions = [county_get_fips(ct, enclosing) for ct in enclosed]
        filename = file_helper.COUNTY
    else:
        raise Exception(f'Invalid level: {level}')
    print('Fetching data')
    df = pd.read_csv(filename)
    print('Data read. Beginning filter')
    latest_date = max(df['DATE_COLUMN1'])
    df = df[df['DATE_COLUMN1'] == latest_date]
    df = df[df['REGIONNAME1'].isin(regions)]
    return df, regions, latest_date


def rent_figure(level, enclosing, enclosed):
    """
    Create a figure comparing rental efficiency across areas
    :param level: enclosed/enclosing e.g. zip/state, county/state
    :param enclosing: Enclosing state. e.g. NC
    :param enclosed: A list of areas at enclosed level within enclosing
    :return:
    """
    def map_calc_mortgage(val):
        YEARLY_INTEREST = 3.33
        # Number of months to pay. Assume 30y loan
        L = 30 * 12
        # Assume home price is loan principle
        P = val
        R = ((YEARLY_INTEREST / 12) * 0.01) + 1

        dividend = (R ** L) * (R - 1)
        divisor = (R ** L) - 1
        payment = P * (dividend / divisor)
        return float('%.2f' % payment)

    def map_get_name(region_name):
        l1 = level.split('/')[0]
        if l1 == 'zip':
            return region_name
        elif l1 == 'city':
            return list(city_cw_df[city_cw_df['UNIQUE_CITY_ID'] == region_name]['CITY'])[0]
        elif l1 == 'county':
            return list(county_cw_df[county_cw_df['FIPS'] == region_name]['COUNTYNAME'])[0]

    print(f'Creating {level} rental value comparison for {enclosing}')
    df, regions, date = filter_level_data(level, enclosing, enclosed)
    df = df[df['MEDIANRENTALPRICE_ALLHOMES1'].notnull() & df['MEDIANLISTINGPRICE_ALLHOMES1'].notnull()]
    df['MonthlyMortgage'] = df['MEDIANLISTINGPRICE_ALLHOMES1'].apply(map_calc_mortgage)
    df['MonthlyProfit'] = df['MEDIANRENTALPRICE_ALLHOMES1'] - df['MonthlyMortgage']
    df['X_axis'] = df['REGIONNAME1'].apply(map_get_name)
    df.sort_values('X_axis')
    try:
        fig = df.plot(x='X_axis', y='MonthlyProfit', kind='bar', figsize=(14, 10))
    except IndexError:
        print('Unable to create figure. Data:')
        print(df)
        print('Likely cause: too many null values for rental and listing price')
        exit(-1)
    plt.xlabel(level.split('/')[0].capitalize(), fontsize=15)
    plt.ylabel('Monthly Profit', fontsize=15)
    plt.suptitle(f'Projected Monthly Rental Profit by {level.split("/")[0].capitalize()} in {enclosing}', fontsize=16)
    f_n = date[:10] + level.replace('/', '_') + '_' + enclosing + '.png'
    plt.tight_layout(pad=2)
    plt.savefig(file_helper.fig_path(f_n))
    print('Figure output at figures/'+f_n)


def home_val_incr(level, enclosing, enclosed):
    """
    Create a figure comparing rental efficiency across areas
    :param level: enclosed/enclosing e.g. zip/state, county/state
    :param enclosing: Enclosing state. e.g. NC
    :param enclosed: A list of areas at enclosed level within enclosing
    :return:
    """
    print(f'Creating {level} home value increase comparison for {enclosing}')
    df, regions, date = filter_level_data(level, enclosing, enclosed)


def city_num_sales(city):
    state = city[-2:]
    city = city[:-2]
    county = city_get_county(city, state)
    state_name = S_NAME_MAP[state]
    city_id = city_get_id(city, state)
    city_data = pd.read_csv(file_helper.CITY)
    city_data = city_data[city_data['REGIONNAME1'] == city_id][['DATE_COLUMN1', 'SALE_COUNTS1']]
    city_data = city_data[city_data['SALE_COUNTS1'].isna() == False].reset_index(drop=True)
    dates = pd.to_datetime(city_data['DATE_COLUMN1']).dt.date
    data = city_data['SALE_COUNTS1']
    fig, ax = plt.subplots()
    ax.plot(data)
    plt.xlabel('Date')
    plt.ylabel('Sale Counts')
    plt.title('Sale Counts by Date for {}, {}'.format(city.title(), state_name.title()))
    ax.set_xticklabels(dates)
    plt.savefig(file_helper.fig_path('sale_counts_{}.png'.format(city.lower())))


def city_county_state(city):
    state = city[-2:]
    city = city[:-2]
    county = city_get_county(city, state)
    state_name = S_NAME_MAP[state]
    city_id = city_get_id(city, state)
    county_id = county_cw_df[(county_cw_df['COUNTYNAME'] == county) &
                       (county_cw_df['STATENAME'] == state_name)]['COUNTY_ID'].values[0]

    city_data = pd.read_csv(file_helper.CITY)
    city_data = city_data[city_data['REGIONNAME1'] == city_id]
    city_data = city_data[['DATE_COLUMN1', 'SALE_COUNTS1']].reset_index(drop=True)

    county_data = pd.read_csv(file_helper.COUNTY)
    county_data = county_data[county_data['COUNTY_ID'] == county_id]
    county_data = county_data[['DATE_COLUMN1', 'SALE_COUNTS1']].reset_index(drop=True)

    state_data = pd.read_csv(file_helper.STATE)
    state_data = state_data[state_data['REGIONNAME1'] == state_name]
    state_data = state_data[['DATE_COLUMN1', 'SALE_COUNTS1']].reset_index(drop=True)

    data_mask = (city_data['SALE_COUNTS1'].isna() == False) & (county_data['SALE_COUNTS1'].isna() == False)
    data_mask = data_mask & (state_data['SALE_COUNTS1'].isna() == False)

    city_data = city_data[data_mask].sort_values('DATE_COLUMN1').reset_index(drop=True)
    county_data = county_data[data_mask].sort_values('DATE_COLUMN1').reset_index(drop=True)
    state_data = state_data[data_mask].sort_values('DATE_COLUMN1').reset_index(drop=True)

    dates = pd.to_datetime(city_data['DATE_COLUMN1']).dt.date.sort_values()
    combined = state_data['SALE_COUNTS1'] + county_data['SALE_COUNTS1']

    fig, ax = plt.subplots()

    ax.bar(range(len(dates)), state_data['SALE_COUNTS1'], label='State')
    ax.bar(range(len(dates)), county_data['SALE_COUNTS1'], bottom=state_data['SALE_COUNTS1'], label='County')
    ax.bar(range(len(dates)), city_data['SALE_COUNTS1'], bottom=combined, label='City')

    ax.set_ylabel('Sale Counts')
    ax.set_xlabel('Date')
    ax.set_title('Sale Counts by Region, {}, {} County, {}'.format(city.title(), county.title(), state_name.title()))
    ax.legend()
    ax.set_xticklabels(dates)
    plt.savefig(file_helper.fig_path('sale_counts_by_region_{}.png'.format(city)))


class ArgParser:

    def __init__(self):
        self.possibilities = {
            'rental': self.rent_parse,
            'city_num_sales': self.city_num_sales,
            'city_county_state': self.city_county_state,
            'home_val_incr': self.home_val_incr
        }
        self.level_options = ['zip/state', 'city/state', 'county/state']
        self.state_codes = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'DC', 'FL', 'GA', 'HI', 'ID', 'IL',
                            'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE',
                            'NV', 'NH', 'NJ', 'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'PR', 'RI', 'SC',
                            'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'VI', 'WA', 'WV', 'WI', 'WY']

    def no_args(self):

        choice = input('Which visualization would you like?: ')
        if choice in self.possibilities:
            self.possibilities[choice]()
        elif choice.lower() == 'y':
            print(*self.possibilities)
            self.no_args()
        elif choice.lower() == 'n':
            exit(0)
        else:
            print('Invalid selection')
            self.no_args()

    def parse_args(self, args):
        try:
            graph = args[0]
        except IndexError:
            self.no_args()
            return
        if graph in self.possibilities:
            try:
                self.possibilities[graph](args[1:])
            except IndexError:
                self.possibilities[graph]()
        else:
            print('Invalid selection')
            self.no_args()

    def loc_parse(self, levels, enclosing):
        levels = levels.lower()
        if levels == 'zip/state':
            return state_get_zips(enclosing)
        elif levels == 'city/state':
            return state_get_cities(enclosing)
        elif levels == 'county/state':
            return state_get_counties(enclosing)
        else:
            print(f'Invalid location levels: {levels}')
            print('Valid options are: zip/state, city/state, county/state')
            return False

    def get_level(self):
        print('Which level comparison would you like?')
        print('Options: ' + ', '.join(self.level_options))
        inp = input('Answer: ')
        if inp.lower() in self.level_options:
            return inp.lower()
        else:
            print('Invalid option')
            return self.get_level()

    def get_state(self):
        print('Enter a state code e.g. NY')
        inp = input('Answer: ').upper()
        if inp in self.state_codes:
            return inp
        else:
            print('Invalid state')
            self.get_state()

    def get_county(self, state):
        print(f'Enter county name (in {state}')
        opt = sorted(state_get_counties(state))
        pretty_print(opt, 5)
        while True:
            inp = input('Answer: ').upper()
            if inp in opt:
                return inp
            else:
                print('Invalid County')

    def get_enclosing(self, level):
        if level == 'state':
            return self.get_state()
        else:
            st = self.get_state()
            county = self.get_county(st)
            return county + st

    def level_parse(self, args=None):
        if args:
            ln = len(args)
        else:
            ln = 0
        if ln == 0:
            level = self.get_level()
            ln += 1
        else:
            level = args[0].lower()
            if level not in self.level_options:
                print('Invalid level option')
                level = self.get_level()
        if ln == 1:
            enclosing = self.get_enclosing(level.split('/')[1])
        else:
            enclosing = args[1]
            if level.split('/')[1] == 'state':
                if enclosing not in self.state_codes:
                    print('Invalid state')
                    enclosing = self.get_enclosing(level.split('/')[1])
            else:
                if enclosing[-2:] not in self.state_codes or enclosing[:-2] not in state_get_counties(enclosing[-2:]):
                    print('Invalid county')
                    enclosing = self.get_enclosing(level.split('/')[1])
        return level, enclosing

    def get_city(self):
        state = self.get_state()
        cities = sorted(state_get_cities(state))
        pretty_print(cities, 5)
        while True:
            print(f'Enter the city from {state}')
            inp = input('Answer: ').upper()
            if inp in cities:
                return inp + state
            else:
                print('Invalid choice')

    def parse_city(self, args):
        if args:
            ln = len(args)
        else:
            ln = 0
        if ln == 0:
            city = self.get_city()
        else:
            city = args[0]
            if city[:-2] not in state_get_cities(city[-2:]):
                city = self.get_city()
        return city

    def rent_parse(self, args=None):
        level, enclosing = self.level_parse(args)
        enclosed = self.loc_parse(level, enclosing)
        rent_figure(level, enclosing, enclosed)

    def city_num_sales(self, args=None):
        city = self.parse_city(args)
        city_num_sales(city)

    def city_county_state(self, args=None):
        city = self.parse_city(args)
        city_county_state(city)

    def home_val_incr(self, args=None):
        level, enclosing = self.level_parse(args)
        enclosed = self.loc_parse(level, enclosing)
        home_val_incr(level, enclosing, enclosed)


if __name__ == '__main__':
    arg_parser = ArgParser()
    try:
        sysargs = sys.argv[1:]
    except IndexError:
        print('No arguments passed. Enter Y to see possibilities or N to cancel')
        arg_parser.no_args()
    else:
        arg_parser.parse_args(sysargs)