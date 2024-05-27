import unittest
import os
import sys
from unittest.mock import MagicMock, patch
module_path = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)
sys.path.append(module_path)

from utils.interface import *
from utils.expiry_checks import *

class TestUtils(unittest.TestCase):
    @patch("pwd.getpwuid")
    @patch("os.stat")
    def test_get_file_creator(self, patch_stat, patch_pwd):
        """
        Tests retrieving the user name of a file owner
        """
        # Successfully retrieves file owner
        patch_stat.return_value.st_uid=5111
        patch_stat.return_value.st_gid=1555
        patch_pwd.return_value.pw_name="tester_account"

        file_creator = get_file_creator("/home/machung/test.txt")
        self.assertEqual(file_creator[0], "tester_account")
        self.assertEqual(file_creator[1], 5111)
        self.assertEqual(file_creator[2], 1555)
        
    @patch('os.stat')
    def test_is_expired_filepath(self, patch_stat):
        """
        Tests the is_expired_file function
        """
        seconds_for_expiry = 30 * 24 * 60 * 60 # 30 days
        patch_stat.st_atime = 5 * 24 * 60 * 60 # 5 days
        patch_stat.st_ctime = 5 * 24 * 60 * 60 # 5 days
        patch_stat.st_mtime = 5 * 24 * 60 * 60 # 5 days
        scrape_time = 50 * 24 * 60 * 60  # 50 days

        # Days since last access is 50 - 5 = 45 > 30
        # The file should be expired
        self.assertTrue(is_expired_filepath("test_name.txt", patch_stat, scrape_time, seconds_for_expiry)[0])

        scrape_time = 10 * 24 * 60 * 60  # change to 10 days
        # Days since last access is 10 - 5 = 5 < 30
        # The file should not be expired
        expiry_test_result =  is_expired_filepath("test_name.txt", patch_stat, scrape_time, seconds_for_expiry)
        self.assertFalse(expiry_test_result[0])
        self.assertTrue(5 * 24 * 3600, expiry_test_result[2])
        self.assertTrue(5 * 24 * 3600, expiry_test_result[3])
        self.assertTrue(5 * 24 * 3600, expiry_test_result[4])

    @patch('os.listdir')
    @patch("os.stat")
    @patch("utils.expiry_checks.is_expired")
    def test_is_expired_folder(self, patch_expired, patch_stat, patch_path):
        """
        Tests the is_expired_folder function. This should return 
        True (is_expired) if all subdirectories and files are also expired. 

        The values of atime, ctime, and mtime should be the largest timestamps 
        seen from the entire folder tree. This indicates the most recent timestamp. 
        In the test we just simulate those timestamps by using smaller integers. 
        """
        mocked_file_expiry_results_1 = MagicMock()
        mocked_file_expiry_results_2 = MagicMock()

        mocked_file_expiry_results_1.configure_mock(
            is_expired = True, creators = ("a", 0, 0), atime = 1000, 
            ctime = 2000, mtime = 10000)
            # atime, ctime, mtime = 5, 7, and 10 days respectively
                
        mocked_file_expiry_results_2.configure_mock(
            is_expired = False, creators = ("b", 1, 1), atime = 2000, 
            ctime = 6000 , mtime = 5000)
           # atime, ctime, mtime = 7, 6, and 15 days respectively
           
        patch_expired.side_effect = [mocked_file_expiry_results_1, 
                                     mocked_file_expiry_results_2]
        patch_path.return_value = ["one.txt", "two.txt"]

        # atime, ctime, mtime for the folder itself is 5 days for all
        patch_stat.st_atime = patch_stat.st_ctime = patch_stat.st_mtime = 3000

        res = is_expired_folder("test_path", patch_stat, 0, 0)
        self.assertEqual(False, res[0])
        self.assertEqual(3000 , res[2])
        self.assertEqual(6000 , res[3])
        self.assertEqual(10000 , res[4])

if __name__ == '__main__':
    unittest.main()