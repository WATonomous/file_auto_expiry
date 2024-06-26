# infra_file_auto_expiry
### Requirement
This project requires sudo priveleges to run

## Purpose
Relating to issue: https://github.com/WATonomous/infra-config/issues/1143

This project is meant to help automatically expire and delete files. It's currently at the stage of gathering all necessary information about file deletion easier. In the future, it is required to add a notification system for users whose files are to be deleted, and an actual deletion system. 

Currently it moves through every single top level folder in a directory, and checks whether it is expired or not. This means that every single file in that directory tree must be expired. As it does this, it gathers all the users who created files in that directory, and the days since the most RECENT atime, ctime, and mtime of ANY file in that directory. It only collects these for folders which have been confirmed to be expired.

## Usage
There are two commands currently, which are associated with the first two stages of the project. 
1. collect-file-info
2. collect-creator-info

### To collect the expiry information of all top level directories in a given path:
```
sudo $(which python3)  /path_to_directory/infra_file_auto_expiry/infra_file_auto_expiry/source/main.py collect-file-info folder_path --days-for-expiry=5
```
Required flags:
    folder_path : STRING | Path to folder to check expiry of
Optional flags:
    --days-for-expiry=x : INT | The amount of days of non-usage that indicates any file is expired. 

This will return a jsonl file of the following form. After the first two dictionary type objects, each dictionary contains the information of ONE top level folder inside of the folder_path flag. AKA. This program reports information by iterating through the top level folders, but checks expiry by entering recursively through each of those folders.  Essentially, each dictionary is associated with a PATH, and all creators who are associated with said path.  
```
{"scrape_time:": x, "scrape_time_datetime": "a datetime"}
{"time_for_scrape_sec": x, "time_for_scrape_min": x}
{"path": "", 
"creators": [list of people who created any file in the folder], 
"expired": Boolean whether the file is expired or not, 
"time_variables": {"atime_datetime": "most recent access datetime", 
                "ctime_datetime": "most recent change datetime", 
                "mtime_datetime": "most recent modification datetime"}}
...
```

### You can then use this in the following command to tabulate all expired paths that are associated with a particular user. 
```
sudo $(which python3)  /path_to_directory/infra_file_auto_expiry/infra_file_auto_expiry/source/main.py collect-creator-info path_to_jsonl_file
```
Required flags:
    path_to_jsonl : STRING | Should be a file that is from calling collect-file-info. 

Optional flags:
    --save-file="" : SRING | A path to a jsonl file to save the collected information to. If this is undefined, then the program will just generate a filename and save it to the working directory. 

This command will return a file of the following form. Essentially, each dictionary is associated with a USER, and all paths that are associated with said user.  
```
{"scrape_time:": x, "scrape_time_datetime": "a datetime"}
{"paths": {"path1": {dictionary of it's atime, ctime, mtime datetimes}, 
        "path2": {dictionary of it's atime, ctime, mtime datetimes}, 
        "pathx": {dictionary of it's atime, ctime, mtime datetimes}}, "name": "username", "uid": "user id", "gid": "user global id"}
...
```