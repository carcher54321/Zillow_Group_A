# file for creating unit tests
import unittest
import prep_file
import os
import logging
logging.basicConfig(filename='test.log', level=logging.INFO)


class PrepFileTests(unittest.TestCase):

    @staticmethod
    def set_data_path(path=None):
        if not path:
            prep_file.DATA_PATH = os.path.join(os.path.dirname(__file__), 'data')
        else:
            prep_file.DATA_PATH = path

    def data_path(self, relative):
        path = os.path.join(os.path.dirname(__file__), 'data')
        self.set_data_path(path)
        return os.path.join(path, relative)

    def test_data_path(self):
        self.set_data_path()
        self.assertEqual(prep_file.data_path('test'),
                         os.path.join(prep_file.DATA_PATH, 'test'))

    def test_log_path(self):
        prep_file.ROOT = os.path.dirname(__file__)
        self.assertEqual(prep_file.log_path('test.csv'),
                         os.path.join(os.path.join(os.path.dirname(__file__), 'logs'), 'test.log'))

    def test_get_data_filenames(self):
        os.mkdir(self.data_path(''))
        with open(self.data_path('test.csv'), 'w') as f:
            f.write('Hey there')
        self.assertEqual(prep_file.get_data_filenames(), ['test.csv'])
        os.remove(self.data_path('test.csv'))
        os.rmdir(self.data_path(''))

    def test_match_filenames(self):
        filenames = ['test.csv', 'happy.csv', 'sad.csv']
        self.assertEqual(prep_file.match_filename(filenames, 'tst.csv'), 'test.csv')
        self.assertEqual(prep_file.match_filename(filenames, 'happy.csv'), 'happy.csv')
        incorrect_file = 'nope'
        with self.assertLogs(level=logging.ERROR) as cm:
            prep_file.match_filename(filenames, incorrect_file)
        self.assertEqual(cm.output, [f'ERROR:root:File {incorrect_file} does not exist in data folder'])

    def test_archive(self):
        pass


if __name__ == '__main__':
    unittest.main()
    os.remove(os.path.join(os.path.dirname(__file__), 'test.log'))
