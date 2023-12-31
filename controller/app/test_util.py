import unittest
import tempfile
import ujson as json


from util import load_config
from util import save_config
from util import LogFormatter
from util import configure_logger
from util import default_config
from logging import FileHandler


class TestUtil(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory
        self._temp_dir = tempfile.TemporaryDirectory()
        self.test_cfg = {
            'test': 123
        }
        self.test_cfg.update(default_config)
        with open(self.config_file_name(), 'w') as f:
            json.dump(self.test_cfg, f)

    def tearDown(self):
        # Remove the directory after the test
        self._temp_dir.cleanup()

    def temp_dir(self):
        return self._temp_dir.name

    def config_file_name(self):
        return f'{self.temp_dir()}/config.json'

    def log_file_name(self):
        return f'{self.temp_dir()}/logfile.txt'

    def test_load_config(self):
        expected = self.test_cfg.copy()
        self.assertEqual(load_config(json.dumps(self.test_cfg)), expected)
        self.assertEqual(load_config(self.test_cfg), expected)
        self.assertEqual(load_config(self.config_file_name()), expected)
        expected['SETTINGS_FILE'] = self.config_file_name()

    def test_load_config_not_found(self):
        filename = 'not-found.json'
        expected = default_config.copy()
        expected['SETTINGS_FILE'] = filename
        expected['SETTINGS_LOAD_STATUS'] = f'File not found "{filename}"'
        self.assertEqual(load_config(filename), expected)

    def test_save_config(self):
        save_config(self.test_cfg, self.config_file_name())
        with open(self.config_file_name(), 'r') as f:
            self.assertEqual(json.load(f), self.test_cfg)

    @unittest.skipUnless(hasattr(unittest.TestCase, 'assertRegex'), "Can't use assertRegex in micropython")
    def test_log_formatter(self):
        formatter = LogFormatter()
        self.assertRegex(formatter.formatTime(datefmt=None, record=None), '[\\d]+\\.[\\d]{3}')

    @unittest.skipUnless(hasattr(unittest.TestCase, 'assertRegex'), "Can't use assertRegex in micropython")
    def test_file_logger(self):
        config = {'LOG_FILE': self.log_file_name()}
        logger = configure_logger(config)

        # remove all the handlers except the file handler
        # this is just so we don't have any console output because for some reason unittest
        # does not capture it
        to_remove = [handler for handler in logger.handlers if not isinstance(handler, FileHandler)]
        for handler in to_remove:
            logger.removeHandler(handler)

        logger.info('test')
        with open(self.log_file_name()) as f:
            output = f.read()
        self.assertRegex(output, '[\\d]+\\.[\\d]{3} test')


if __name__ == '__main__':
    unittest.main()
