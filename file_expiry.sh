#!/bin/bash

set -e

PYTHON=$(which python) # get python location
MAIN_SCRIPT=$(realpath "infra_file_auto_expiry/source/main.py")
STORAGE_FOLDER=""

echo "Automatic File Expiry Tool"
echo "Removes expired files"
echo "Specify arguments folder path and the days for expiry of your files"
echo "Python location is: $PYTHON"
echo "Running $MAIN_SCRIPT"

python $MAIN_SCRIPT "$@"