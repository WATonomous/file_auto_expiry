import os
import pwd
import json
import datetime
import time
from ..data.expiry_constants import *
from ..data.tuples import *
from .expiry_checks import is_expired

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

def scan_folder_for_expired(folder_path, expiry_threshold):
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
            expiry_result = is_expired(entry.path, expiry_threshold)
            # path, creator tuple (name, uid, gid), atime, ctime, mtime
            yield entry.path, expiry_result.is_expired, expiry_result.creators, \
                expiry_result.atime, expiry_result.ctime, expiry_result.mtime

def collect_expired_file_information(folder_path, save_file, scrape_time, expiry_threshold):
    """
    Interface function which collects which directories are 'expired'

    String folder_path: The folder to scan for expired files
    String save_file: The jsonl file path to save the information to, 
    ie "path_name.jsonl"
    Int scrape_time: the time at the start of the information scrape
    Int seconds_for_expiry: The amount of days since last usage that indicates 
    expiry
    """
    if not os.path.isdir(folder_path):
        raise Exception("Base folder does not exist")
    
    if not save_file:
        # save_file path not given
        save_file = f"file_information_{str(datetime.datetime.fromtimestamp(scrape_time))}.jsonl"

    path_info = dict()
    for path, is_expired, creators, atime, ctime, mtime in scan_folder_for_expired(
        folder_path, expiry_threshold):
        # handles generating the dictionary

        path_info[path] = { 
            "path": path, # storing pathname so we keep it when we transfer the dictionary to jsonl
            "creators": [creator for creator in creators],
            "expired": is_expired,
            "time_variables": {
                "atime_datetime": str(datetime.datetime.fromtimestamp(atime)),
                "ctime_datetime": str(datetime.datetime.fromtimestamp(ctime)),
                "mtime_datetime": str(datetime.datetime.fromtimestamp(mtime)),
            }}        
    
    write_jsonl_information(path_info, save_file, scrape_time)

def write_jsonl_information(dict_info, file_path, scrape_time):
    current_time = time.time()

    with open(file_path, "w") as file:
        file.write(json.dumps({"scrape_time:": scrape_time,
                               "scrape_time_datetime": str(datetime.datetime.fromtimestamp(scrape_time))}) + "\n")
        file.write(json.dumps({"time_for_scrape_sec": current_time - scrape_time,
                               "time_for_scrape_min": (current_time - scrape_time) / 60}) + "\n")
        
        for key in dict_info:
            file.write(json.dumps(dict_info[key]) + "\n") 

def collect_creator_information(path_info_file, save_file, scrape_time):
    """
    Returns a dictionary relating path information to each creator
    Must be given the return value of form similar to the output of 
    collect_expired_file_information()

    String path_info_file: A jsonl file path containing information about a 
    certain path. This should be the result of calling the collect_file_information
    function.

    String save_file: The jsonl file path to save the information to, 
    ie "path_name.jsonl"

    Int scrape_time: The time at the start of the information scrape. 
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
                # take all unique creators and make a new dictionary about them
                for user in path_data["creators"]:
                    time_vars = path_data["time_variables"]
                    if user[1] in creator_info:
                        creator_info[user[1]]["paths"][path_data["path"]] = time_vars
                        
                    else:
                        creator_info[user[1]] = {
                            "paths": {path_data["path"]: time_vars}, 
                            "name": user[0],
                            "uid": user[1],
                            "gid": user[2]}
        
    write_jsonl_information(creator_info, save_file, scrape_time)
