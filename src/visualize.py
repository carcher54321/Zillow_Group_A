import cx_Oracle as orc
import sys
import os


orc.init_oracle_client(lib_dir=r'C:\Users\carch\Desktop\instantclient_19_10')
S_FIPS_MAP = {
    'MS': 28, 'WV': 54, 'MI': 26, 'AL': 1, 'NM': 35, 'OK': 40, 'VT': 50, 'TN': 47, 'RI': 44, 'WI': 55, 'NY': 36,
    'DC': 11, 'CT': 9, 'NE': 31, 'WY': 56, 'VA': 51, 'MD': 24, 'HI': 15, 'MT': 30, 'ID': 16, 'KY': 21, 'KS': 20,
    'LA': 22, 'AK': 2, 'CO': 8, 'PA': 42, 'OR': 41, 'NC': 37, 'IN': 18, 'MO': 29, 'AR': 5, 'ME': 23, 'NH': 33, 'CA': 6,
    'OH': 39, 'MA': 25, 'NJ': 34, 'IL': 17, 'SD': 46, 'SC': 45, 'TX': 48, 'AZ': 4, 'UT': 49, 'WA': 53, 'FL': 12,
    'NV': 32, 'DE': 10, 'GA': 13, 'MN': 27, 'IA': 19, 'ND': 38
}


class TableInfo:

    def __init__(self, table_name, region_header):
        self.name = table_name
        self.region_header = region_header


class DbInfo:

    def __init__(self):
        self.STATE = TableInfo('T_State_time_series', 'RegionName')
        self.CITY = TableInfo('T_City_time_series', 'RegionName')
        self.COUNTY = TableInfo('T_County_time_series', 'RegionName')
        self.METRO = TableInfo('T_Metro_time_series', 'RegionName')
        self.NEIGHBORHOOD = TableInfo('T_Neighborhood_time_series', 'RegionName')
        self.ZIP = TableInfo('T_Zip_time_series', 'RegionName')
        self.COUNTY_CW = TableInfo('T_COUNTYCROSSWALK_ZILLOW', '')
        self.CITY_CW = TableInfo('T_CITIES_CROSSWALK', '')


class DbConn:

    def __init__(self):
        self.dsn = orc.makedsn('174.104.164.39', '1521', service_name='orcl')
        self.user = 'ali_adam'
        self.password = 'root'

        self.db = orc.connect(
            user=self.user,
            password=self.password,
            dsn=self.dsn
        )
        self.cur = self.db.cursor()

    def __del__(self):
        self.cur.close()
        self.db.close()

    def cursor(self):
        return self.db.cursor()

    def execute(self, sql):
        self.cur.execute(sql)


DB_INF = DbInfo()
CONN = DbConn()


def pretty_print(lis, per_line):
    i = 0
    ln = len(lis)
    while i + per_line < ln:
        print(*lis[i:i+per_line])
        i += per_line
    if i < ln - 1:
        print(*lis[i:])


def get_regions(table):
    cursor = CONN.cursor()
    cursor.execute(f'SELECT DISTINCT {table.region_header} FROM {table.name};')
    return cursor.fetchall()


def get_region_data(table, region):
    cursor = CONN.cursor()
    cursor.execute(f'SELECT * FROM {table.name} WHERE {table.region_header}={region}')
    return cursor.fetchall()


def county_get_fips(county, st):
    cursor = CONN.cursor()
    cursor.execute('SELECT FIPS FROM T_COUNTYCROSSWALK_ZILLOW WHERE COUNTYNAME=(:county) AND STATEFIPS=(:s_fips)', [county, S_FIPS_MAP[st]])
    fips = cursor.fetchone()
    return fips[0]


def city_get_id(city, st):
    cursor = CONN.cursor()
    cursor.execute('SELECT UNIQUE_CITY_ID FROM T_CITIES_CROSSWALK WHERE CITY=(:city) and STATE_ABBR=(:s)', [city, st])
    ident = cursor.fetchone()
    return ident[0]


def city_get_county(city, st):
    cursor = CONN.cursor()
    cursor.execute('SELECT COUNTY FROM T_CITIES_CROSSWALK WHERE CITY=(:city) and STATE_ABBR=(:s)', [city, st])
    county_n = cursor.fetchone
    return county_n[0]


def state_get_counties(st):
    cursor = CONN.cursor()
    cursor.execute('SELECT COUNTYNAME FROM T_COUNTYCROSSWALK_ZILLOW WHERE STATEFIPS=(:s_fips)', [S_FIPS_MAP[st]])
    counties = cursor.fetchall()
    return [s[0] for s in counties]


def state_get_cities(st):
    cursor = CONN.cursor()
    cursor.execute('SELECT CITY from T_CITIES_CROSSWALK WHERE STATE_ABBR = (:s_abbr)', [st])
    cities = cursor.fetchall()
    return [s[0] for s in cities]


def state_get_zips(st):
    cursor = CONN.cursor()
    cursor.execute('SELECT ZIP FROM T_CITITES_CROSSWALK WHERE STATE_ABBR=(s_abbr) AND ZIP IS NOT NULL', [st])
    zips = cursor.fetchall()
    return [s[0] for s in zips]


def rent_figure(level, enclosing, enclosed):
    """
    Create a figure comparing rental efficiency across areas
    :param level: enclosed/enclosing e.g. zip/state, county/state
    :param enclosing: Enclosing state. e.g. NC
    :param enclosed: A list of areas at enclosed level within enclosing
    :return:
    """
    pass


# city format cityST e.g. newyorkNY
def city_num_sales(city):
    pass


# city format cityST e.g. newyorkNY
def city_county_state(city):
    state_abbr = city[-2:]
    city = city[:-2]
    city_id = city_get_id(city, state_abbr)
    county_fips = county_get_fips(city_get_county(city, state_abbr), state_abbr)


def home_val_incr(level, enclosing, enclosed):
    """
    Create a figure comparing rental efficiency across areas
    :param level: enclosed/enclosing e.g. zip/state, county/state
    :param enclosing: Enclosing state. e.g. NC
    :param enclosed: A list of areas at enclosed level within enclosing
    :return:
    """
    pass


class ArgParser:

    def __init__(self):
        self.possibilities = {
            'rental': self.rent_parse,
            'city_num_sales': self.city_num_sales,
            'city_county_state': self.city_county_state,
            'home_val_incr': self.home_val_incr
        }
        self.level_options = ['zip/state', 'city/state', 'county/state', 'zip/county']
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
        elif choice.lower() == 'n':
            exit(0)
        else:
            print('Invalid selection')
            self.no_args()

    def parse_args(self, args):
        graph = args[0]
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
        opt = state_get_counties(state)
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
        cities = state_get_cities(state)
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
        arg_parser.parse_args(sysargs)
    except IndexError:
        print('No arguments passed. Enter Y to see possibilities or N to cancel')
        arg_parser.no_args()
