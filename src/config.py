import os

ROOT = os.path.dirname(os.path.dirname(__file__))
TAR_PATH = os.path.join(ROOT, 'data_archive.tar')
EMAIL_SENDER = 'carcher.djangodev@gmail.com'
DB_EMAIL_SENDER = 'lucas.invernizzi@gmail.com'
FILE_NAME_ACCURACY = 0.9
EMAIL_RECIPIENTS = [
    'colin.archer@smoothstack.com',
    'lucas.invernizzi@smoothstack.com'
]
DATA_PATH = os.path.join(ROOT, 'data')
OUT_PATH = os.path.join(ROOT, 'output')
FILE_NAMES = [
    'cities_crosswalk.csv',
    'City_time_series.csv',
    'County_time_series.csv',
    'CountyCrossWalk_Zillow.csv',
    'Metro_time_series.csv',
    'Neighborhood_time_series.csv',
    'State_time_series.csv',
    'Zip_time_series.csv'
]
NAN_REPLACE = 'Nan'
DB_HOST = 'zillowa.c5djwvyj87zw.us-east-2.rds.amazonaws.com'
DB_PORT = '1521'
DB_SERVICE = 'zillowdb'
DB_USER = 'admin'
DB_PASS = 'rootuser123'
