from utils import *
import sys


def main(base_folder):
    delete_expired_files(base_folder)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python file_expiry.py <folder to scan>")
        sys.exit(1)

    base_folder = sys.argv[1]
    main(base_folder=base_folder)