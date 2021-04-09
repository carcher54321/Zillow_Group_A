import os
import logging
from difflib import SequenceMatcher
import tarfile
import gmail_connect
import sys
from FileValidation import FileValidation

# usage: python prep_file [DATA_PATH] [FILE_NAME (not path)] [OUT_PATH]

FILE_NAME = 'City_time_series.csv'
FILE_NAME_ACCURACY = 0.9
EXTENSION = FILE_NAME.split('.')[-1]
ROOT = os.path.dirname(os.path.dirname(__file__))
TAR_PATH = os.path.join(ROOT, 'data_archive.tar')
EMAIL_SENDER = 'carcher.djangodev@gmail.com'
EMAIL_RECIPIENTS = ['colin.archer@smoothstack.com']
DATA_PATH = os.path.join(ROOT, 'data')
OUT_PATH = os.path.join(ROOT, 'output')


def data_path(relative):
    return os.path.join(DATA_PATH, relative)


def log_path():
    return os.path.join(os.path.join(ROOT, 'logs'), ''.join(FILE_NAME.split('.')[:-1]) + '.log')


def get_data_filenames():
    filenames = [f for f in os.listdir(data_path('')) if os.path.isfile(data_path(f))]
    return filenames


def match_filename(filenames, file):
    file_name = None
    if file not in filenames:
        logging.info(f'Unable to find file {file}, checking data folder for close matches')
        for f in filenames:
            if SequenceMatcher(a=f, b=file).ratio() > FILE_NAME_ACCURACY:
                file_name = f
                logging.info(f'Match found! {file_name}')
                break
        else:
            logging.error(f'File {file} does not exist in data folder')
    else:
        file_name = file
    return file_name


def archive(file_name):
    with tarfile.TarFile(TAR_PATH, 'a') as tar:
        tar.add(data_path(file_name))


def main():
    logging.basicConfig(filename=log_path(), level=logging.INFO, format='%(asctime)s %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p::')
    filenames = get_data_filenames()
    file_name = match_filename(filenames, FILE_NAME)
    if not file_name:
        logging.error('File not found. Unable to continue, exiting.')
        return
    extension = file_name.split('.')[-1]
    if not extension == EXTENSION:
        logging.error(f'The file {file_name} has the wrong extension. Should be .{EXTENSION}')
        logging.info(f'Will attempt to parse anyway')
    validator = FileValidation(data_path(file_name))
    success = validator.validate()
    if success:
        logging.info(f'File Pre-validation successful. Beginning Database Stage')
        db_succ = validator.db_stage()
        if db_succ:
            logging.info(f'Successfully staged into database. Archiving to .tar')
            archive(file_name)
            logging.info(f'Archival success')
            validator.save_to_csv(os.path.join(OUT_PATH, file_name))
    else:
        gmail_connect.sendEmail(EMAIL_SENDER, validator.get_errors(), '', EMAIL_RECIPIENTS,
                                [data_path(file_name), log_path()])


if __name__ == '__main__':
    try:
        DATA_PATH = sys.argv[1]
        logging.info(f'Data path is {DATA_PATH}')
    except IndexError:
        logging.error(f'No Data path passed. Using default')
    try:
        FILE_NAME = sys.argv[2]
        EXTENSION = FILE_NAME.split('.')[-1]
        logging.info(f'Beginning validation of file {FILE_NAME}')
    except IndexError:
        logging.error(f'No file name passed, using default {FILE_NAME}')
    try:
        OUT_PATH = sys.argv[3]
        logging.info(f'Data output path is {OUT_PATH}')
    except IndexError:
        logging.error('No output path passed. Using default')
    main()
