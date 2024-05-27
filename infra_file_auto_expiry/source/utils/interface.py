import os
import pwd
import json
import datetime
import time
from data.expiry_constants import *
from data.tuples import *
from utils.expiry_checks import is_expired

def get_file_creator(path):
    """
    Returns a tuple including the file creator username, 
    their UID, and GID in that order respectively. 

    string file_path: The absolute path of the file
    """
    # Get the UID of the file or directory owner
    # Get the username associated with the UID
    try:
        username = pwd.getpwuid(os.stat(path).st_uid).pw_name
    except KeyError:
        """ FIX THIS LATER"""
        return f"user{os.stat(path).st_uid}"
    return creator_tuple(username, os.stat(path).st_uid, os.stat(path).st_gid)

def notify_file_creators():
    """
    TODO: implement proper notification system
    Currently is just the code to print information to a text file
    """

def scan_folder_for_expired(folder_path, scrape_time, seconds_for_expiry):
    """Generator function which iterates the expired top level folders
    in a given directory.
    
    Collects expiry information including:
    - all contributing users in the folder
    - the days since the most recent atime, ctime, and mtime of the entire folder
    """
    if not os.path.isdir(folder_path) :
        raise Exception("Given path directory "+ folder_path)
    for entry in os.scandir(folder_path):
        if os.path.exists(entry.path):
            expiry_result = is_expired(entry.path, scrape_time, seconds_for_expiry)
            print(entry.path)
            # path, creator tuple (name, uid, gid), atime, ctime, mtime
            yield entry.path, expiry_result.is_expired, expiry_result.creators, \
                expiry_result.atime, expiry_result.ctime, expiry_result.mtime

def collect_expired_file_information(folder_path, save_file, scrape_time, seconds_for_expiry):
    """
    Interface function which collects which directories are 'expired'

    String folder_path: The folder to scan for expired files
    String save_file: The jsonl file path to save the information to, ie "path_name.jsonl"
    int seconds_for_expiry: The amount of days since last usage that indicates expiry
    """
    if not os.path.isdir(folder_path):
        raise Exception("Base folder does not exist")
    
    if not save_file:
        # save_file path not given
        save_file = f"file_information_{str(datetime.datetime.fromtimestamp(scrape_time))}.jsonl"

    path_info = dict()
    for path, is_expired, creators, atime, ctime, mtime in scan_folder_for_expired(folder_path, scrape_time, seconds_for_expiry):
        # handles generating the dictionary

        path_info[path] = { 
            "path": path, # storing pathname so we keep it when we transfer the dictionary to jsonl
            "creators": [creator for creator in creators],
            "expired": is_expired,
            "time_variables": {
                "atime_unix": atime,
                "ctime_unix": ctime,
                "mtime_unix": mtime,
                "atime_datetime": str(datetime.datetime.fromtimestamp(atime)),
                "ctime_datetime": str(datetime.datetime.fromtimestamp(ctime)),
                "mtime_datetime": str(datetime.datetime.fromtimestamp(mtime)),
            }}        
    
    write_jsonl_information(path_info, save_file, scrape_time)
    return save_file 

def write_jsonl_information(dict_info, file_path, scrape_time):
    current_time = time.time()

    with open(file_path, "w") as file:
        file.write(json.dumps({"scrape_time:": scrape_time,
                               "scrape_time_datetime": str(datetime.datetime.fromtimestamp(scrape_time))}) + "\n")
        file.write(json.dumps({"time_for_scrape_sec": current_time - scrape_time,
                               "time_for_scrape_min": (current_time - scrape_time) / 60}))
        
        for key in dict_info:
            file.write(json.dumps(dict_info[key]) + "\n") 

def collect_creator_information(path_info_file, save_file, scrape_time):
    """
    Returns a dictionary relating path information to each creator
    Must be given the return value of form similar to the output of 
    collect_expired_file_information()

    String save_file: The jsonl file path to save the information to, ie "path_name.jsonl"
    """
    if not os.path.exists(path_info_file):
        raise Exception("Given file for path information does not exist")

    if not save_file:
        # save_file path not given
        save_file = f"creator_information_{str(datetime.datetime.fromtimestamp(scrape_time))}.jsonl"

    creator_info = dict()
    with open(path_info_file, "r+") as file:
        lines = file.readlines()

    for line in lines[2:]:
            # One jsonl line of path inforamtion
            path_data = json.loads(line)
            # check if the path is expired
            if path_data["expired"]:
                print("woo")
                # take all unique creators and make a new dictionary about them
                for user in path_data["creators"]:
                    if user[1] in creator_info:
                        time_vars = path_data["time_variables"]
                        creator_info[user[1]]["paths"][path_data["path"]] = time_vars
                        creator_info[user[1]]["recent_time_days"] = min([
                                time_vars["atime"],
                                time_vars["ctime"],
                                time_vars["mtime"],
                                creator_info[user[1]]["recent_time_days"]
                            ]) / SECS_PER_DAY
                    else:
                        creator_info[user[1]] = {
                            "paths": {path_data["path"]: time_vars}, 
                            "name": user[0],
                            "uid": user[1],
                            "gid": user[2],
                            "recent_time_days": min([
                                time_vars["atime"],
                                time_vars["ctime"],
                                time_vars["mtime"]
                            ]) / SECS_PER_DAY}
        
    write_jsonl_information(creator_info, save_file, scrape_time)
    return save_file
