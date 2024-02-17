import pytest
import unittest
import os
import time
import sys
import subprocess
from unittest.mock import patch

module_path = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)
sys.path.append(module_path)

from source.utils import *


class TestFileExpiry(unittest.TestCase):
    @patch("subprocess.run")
    def test_get_file_creator(self, patch_sub):
        """
        Tests retrieving the user name of a file owner
        """
        # Successfully retrieves file owner
        patch_sub.return_value.stdout = "-rw-rw-r-- 1 machung machung 4 Feb 17 05:14 /home/machung/test.txt".encode()
        patch_sub.return_value.stderr = "".encode()
        self.assertEqual(get_file_creator("/home/machung/test.txt"), "machung")

        # Error in retrieving file owner name
        patch_sub.return_value.stderr = "error".encode()
        self.assertEqual(get_file_creator("/home/machung/test.txt"), None)

    @patch('os.stat')
    @patch('time.time')
    def test_is_expired_file(self, patch_time, patch_os):
        """
        Tests the is_expired_file function
        """
        time_to_expire_days = 30
        patch_os.return_value.st_atime = 5 * 24 * 60 * 60
        patch_time.return_value = 50 * 24 * 60 * 60 
        
        # Days since last access is 50 - 5 = 45 > 30
        # The file should be expired
        self.assertTrue(is_expired_file("test_name", time_to_expire_days))

        patch_time.return_value = 10 * 24 * 60 * 60 
        # Days since last access is 10 - 5 = 5 < 30
        # The file should not be expired
        self.assertFalse(is_expired_file("test_name", time_to_expire_days))

    def test_notify_file_creator(self):
        pass
if __name__ == '__main__':
    unittest.main()