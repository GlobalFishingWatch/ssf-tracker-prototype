import unittest
import tempfile
# import shutil
# from pathlib import Path
import json


from config import load_cofig
from config import save_config



class TestConfig(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory
        # self.test_dir = tempfile.mkdtemp()
        self.test_dir = tempfile.TemporaryDirectory()
        self.test_cfg = {
            'test': 123
        }
        with open(self._file_name(), 'w') as f:
            json.dump(self.test_cfg, f)

    def tearDown(self):
        # Remove the directory after the test
        # shutil.rmtree(self.test_dir)
        self.test_dir.cleanup()

    def _file_name(self):
        return f'{self.test_dir.name}/config.json'
        # return Path(self.test_dir.name) / 'config.json'

    def test_load_config(self):
        config = load_cofig(self._file_name())
        self.assertEqual(config, self.test_cfg)

    def test_load_config_not_fount(self):
        config = load_cofig('not-found.json')
        self.assertEqual(config, {})

    def test_save_config(self):
        save_config(self.test_cfg, self._file_name())
        with open(self._file_name(), 'r') as f:
            self.assertEqual(json.load(f), self.test_cfg)

if __name__ == '__main__':
    unittest.main()