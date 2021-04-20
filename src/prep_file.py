import os
import logging
from difflib import SequenceMatcher
import tarfile
import gmail_connect
from FileValidation import FileValidation
import config


FILE_NAMES = config.FILE_NAMES
ROOT = config.ROOT
TAR_PATH = config.TAR_PATH
EMAIL_SENDER = config.EMAIL_SENDER
EMAIL_RECIPIENTS = config.EMAIL_RECIPIENTS
DATA_PATH = config.DATA_PATH
OUT_PATH = config.OUT_PATH


def data_path(relative):
    return os.path.join(DATA_PATH, relative)


def log_path(filename):
    return os.path.join(os.path.join(ROOT, 'logs'), ''.join(filename.split('.')[:-1]) + '.log')


def get_data_filenames():
    filenames = [f for f in os.listdir(data_path('')) if os.path.isfile(data_path(f))]
    return filenames


def match_filename(filenames, file):
    file_name = None
    if file not in filenames:
        logging.info(f'Unable to find file {file}, checking data folder for close matches')
        for f in filenames:
            if SequenceMatcher(a=f, b=file).ratio() > config.FILE_NAME_ACCURACY:
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


def process_file(filename):
    logging.basicConfig(filename=log_path(filename), level=logging.INFO, format='%(asctime)s %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p::')
    filenames = get_data_filenames()
    file_name = match_filename(filenames, filename)
    EXTENSION = filename.split('.')[-1]
    if not file_name:
        logging.error('File not found. Unable to continue, exiting.')
        gmail_connect.sendEmail(EMAIL_SENDER, 'File Not Found', f'{filename} was not found in the data folder',
                                EMAIL_RECIPIENTS, [log_path(filename)])
        return None
    extension = file_name.split('.')[-1]
    if not extension == EXTENSION:
        logging.error(f'The file {file_name} has the wrong extension. Should be .{EXTENSION}')
        logging.info(f'Will attempt to parse anyway')
    validator = FileValidation(data_path(file_name))
    success = validator.validate()
    if success:
        logging.info(f'File Pre-validation successful. Archiving to .tar')
        archive(file_name)
        logging.info(f'Archival success. Saving to output path')
        validator.save_to_csv(os.path.join(OUT_PATH, file_name))
        return log_path(filename)
    else:
        gmail_connect.sendEmail(EMAIL_SENDER, validator.get_errors(), '', EMAIL_RECIPIENTS,
                                [data_path(file_name), log_path(filename)])
        return None


def main():
    log_files = []
    success_filenames = []
    for fn in FILE_NAMES:
        rt = process_file(fn)
        if rt:
            log_files.append(rt)
            success_filenames.append(fn)
    gmail_connect.sendEmail(EMAIL_SENDER, f'Successfully Validated {len(success_filenames)} Files',
                            f'{success_filenames} all validated successfully', EMAIL_RECIPIENTS, log_files)


if __name__ == '__main__':
    main()
