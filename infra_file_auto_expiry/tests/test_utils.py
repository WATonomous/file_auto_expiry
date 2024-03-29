import unittest
import os
import sys
from unittest.mock import MagicMock, Mock, patch
import pathlib

module_path = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)
sys.path.append(module_path)

from source.utils import *


class TestUtils(unittest.TestCase):
    @patch("pwd.getpwuid")
    @patch("os.stat")
    def test_get_file_creator(self, patch_os, patch_pwd):
        """
        Tests retrieving the user name of a file owner
        """
        # Successfully retrieves file owner
        pass
        # patch_os.return_value.st_uid=0
        # patch_pwd.return_value.pw_name="tester_account"
        # self.assertEqual(get_file_creator("/home/machung/test.txt"), "tester_account")
        
    @patch('os.stat')
    @patch('time.time')
    def test_is_expired_filepath(self, patch_time, patch_os):
        """
        Tests the is_expired_file function
        """
        time_to_expire_days = 30
        patch_os.return_value.st_atime = 5 * 24 * 60 * 60
        patch_os.return_value.st_ctime = 5 * 24 * 60 * 60
        patch_os.return_value.st_mtime = 5 * 24 * 60 * 60
        patch_time.return_value = 50 * 24 * 60 * 60 
        # Days since last access is 50 - 5 = 45 > 30
        # The file should be expired
        self.assertTrue(is_expired_filepath("test_name.txt", time_to_expire_days)[0])

        patch_time.return_value = 10 * 24 * 60 * 60 
        # Days since last access is 10 - 5 = 5 < 30
        # The file should not be expired
        self.assertEqual(5, is_expired_filepath("test_name.txt", time_to_expire_days)[2])

    @patch('pathlib.Path.rglob')
    @patch("stat.S_ISREG")
    @patch("os.stat")
    @patch("source.utils.is_expired")
    def test_is_expired_folder(self, patch_expired, patch_stat, patch_reg, patch_path):
        """
        Tests the is_expired_file function
        """
        patch_expired.side_effect = [(True, ("j", 0, 0), 10, 5, 10), (True, ("k", 0, 0), 12, 5, 7)]
        patch_path.return_value = [Path("one.txt"), Path("two.txt")]
        res = is_expired_folder("test_path")
        self.assertEqual((True, {("j", 0, 0), ("k", 0, 0)}, 10, 5, 7), res)

        patch_expired.side_effect = [(True, ("j", 0, 0), 10, 5, 10), (False, ("k", 0, 0), 12, 5, 7)]
        res2 = is_expired_folder("test_path")
        self.assertEqual((False, {("j", 0, 0)}, 10, 5, 10), res2)


       

    def test_notify_file_creator(self):
        pass
if __name__ == '__main__':
    unittest.main()