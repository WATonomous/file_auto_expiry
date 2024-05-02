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
        patch_os.return_value.st_uid=5111
        patch_os.return_value.st_gid=1555
        patch_pwd.return_value.pw_name="tester_account"

        file_creator = get_file_creator("/home/machung/test.txt")
        self.assertEqual(file_creator[0], "tester_account")
        self.assertEqual(file_creator[1], 5111)
        self.assertEqual(file_creator[2], 1555)
        
    @patch('os.stat')
    def test_is_expired_filepath(self, patch_os):
        """
        Tests the is_expired_file function
        """
        seconds_for_expiry = 30 * 24 * 60 * 60 # 30 days
        patch_os.st_atime = 5 * 24 * 60 * 60 # 5 days
        patch_os.st_ctime = 5 * 24 * 60 * 60 # 5 days
        patch_os.st_mtime = 5 * 24 * 60 * 60 # 5 days
        current_time = 50 * 24 * 60 * 60  # 50 days

        # Days since last access is 50 - 5 = 45 > 30
        # The file should be expired
        self.assertTrue(is_expired_filepath("test_name.txt", patch_os, current_time, seconds_for_expiry)[0])

        current_time = 10 * 24 * 60 * 60  # change to 10 days
        # Days since last access is 10 - 5 = 5 < 30
        # The file should not be expired
        expiry_test_result =  is_expired_filepath("test_name.txt", patch_os, current_time, seconds_for_expiry)
        self.assertFalse(expiry_test_result[0])
        self.assertTrue(5 * 24 * 3600, expiry_test_result[2])
        self.assertTrue(5 * 24 * 3600, expiry_test_result[3])
        self.assertTrue(5 * 24 * 3600, expiry_test_result[4])
    
    @patch('os.stat')
    @patch('os.path.islink')
    @patch("source.utils.is_expired_filepath")
    def test_is_expired_link(self, patch_expired, patch_link, patch_os):
        """
        Tests the is_expired_link function. This returns True (is expired) when
        both the link and the true path it points to are both expired. It returns
        False if both or either is NOT expired. 
        """
        patch_link.return_value = True

        mocked_file_expiry_results_1 = MagicMock()
        mocked_file_expiry_results_2 = MagicMock()

        # File expiry mock results: Setting timestamps to 0 for all because we 
        # already test these.
        mocked_file_expiry_results_1.configure_mock(is_expired = True, creators = (), 
                                                    atime = 0, ctime = 0, mtime = 0)
        mocked_file_expiry_results_2.configure_mock(is_expired = False, creators = (), 
                                                    atime = 0, ctime = 0, mtime = 0)
        
        patch_expired.side_effect = [mocked_file_expiry_results_1, 
                                     mocked_file_expiry_results_2]
        
        # Either Link or True path is not expired: Should return False, not expired
        res = is_expired_link("test_path", patch_os, 0, 0)
        self.assertFalse(res[0])

        mocked_file_expiry_results_2.configure_mock(is_expired = True, creators = (),
                                                    atime = 0, ctime = 0, mtime = 0)
        patch_expired.side_effect = [mocked_file_expiry_results_1, 
                                     mocked_file_expiry_results_2]
        
        # Either Link or True path is not expired: Should return False, not expired
        res = is_expired_link("test_path", patch_os, 0, 0)
        self.assertTrue(res[0])

    @patch('pathlib.Path.rglob')
    @patch("os.stat")
    @patch("source.utils.is_expired")
    def test_is_expired_folder(self, patch_expired, patch_os, patch_path):
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
        patch_path.return_value = [Path("one.txt"), Path("two.txt")]

        # atime, ctime, mtime for the folder itself is 5 days for all
        patch_os.st_atime = patch_os.st_ctime = patch_os.st_mtime = 3000

        res = is_expired_folder("test_path", patch_os, 0, 0)
        self.assertEqual(False, res[0])
        self.assertEqual(3000 , res[2])
        self.assertEqual(6000 , res[3])
        print(res)
        self.assertEqual(10000 , res[4])

if __name__ == '__main__':
    unittest.main()