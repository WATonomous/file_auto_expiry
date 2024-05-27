# infra_file_auto_expiry

Relating to issue: https://github.com/WATonomous/infra-config/issues/1143

This project is meant to help automatically expire and delete files. It's currently at the stage of gathering all necessary information about file deletion easier. In the future, it is required to add a notification system for users whose files are to be deleted, and an actual deletion system. C

Currently it moves through every single top level folder in a directory, and checks whether it is expired or not. This means that every single file in that directory tree must be expired. As it does this, it gathers all the users who created files in that directory, and the days since the most RECENT atime, ctime, and mtime of ANY file in that directory. It only collects these for folders which have been confirmed to be expired.

To collect the expiry information of all top level directories in a given path:
sudo $(which python3)  /path_to_directory/infra_file_auto_expiry/infra_file_auto_expiry/source/main.py collect-file-info path_to_check_expiry_of

This will return a jsonl file. You can then use this in the following command to tabulate all expired paths that are associated with a particular user. 

sudo $(which python3)  /path_to_directory/infra_file_auto_expiry/infra_file_auto_expiry/source/main.py collect-creator-info path_to_jsonl_file