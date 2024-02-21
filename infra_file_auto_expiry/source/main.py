from utils import *
import sys


def main(base_folder):
    delete_expired_files(base_folder, temp_folder, 0)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        
        print("Usage: python file_expiry.py <folder to scan> <temp>")
        sys.exit(1)

    base_folder = sys.argv[1]
    temp_folder = sys.argv[2]

    main(base_folder=base_folder)