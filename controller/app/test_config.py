import unittest
import tempfile
import json


from config import load_config
from config import save_config
from config import LogFormatter
from config import configure_logger
from logging import FileHandler


class TestConfig(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory
        self._temp_dir = tempfile.TemporaryDirectory()
        self.test_cfg = {
            'test': 123
        }
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
        config = load_config(self.config_file_name())
        self.assertEqual(config, self.test_cfg)

    def test_load_config_not_fount(self):
        config = load_config('not-found.json')
        self.assertEqual(config, {})

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
        config = {'log-file': self.log_file_name()}
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
