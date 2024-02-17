#!/bin/bash

set -e

PYTHON=$(which python) # get python location
MAIN_SCRIPT=$(realpath "infra_file_auto_expiry/source/main.py")
STORAGE_FOLDER="/home/machung/infra_file_auto_expiry/infra_file_auto_expiry/test"

echo "Automatic File Expiry Tool"
echo "Removes expired files - unused for 30 days or more"
echo "Python location is: $PYTHON"
echo "Running $MAIN_SCRIPT"

(crontab -l ; echo "0 0 * * * $PYTHON $MAIN_SCRIPT \"$STORAGE_FOLDER\"") | crontab -