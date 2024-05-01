import pwd
import shutil
import os
import sys
import time
from pathlib import Path
import stat
import json
import datetime
from collections import namedtuple

expiry_tuple = namedtuple("file_tuple", "is_expired, creators, atime, ctime, mtime")
creator_tuple = namedtuple("creator_tuple", "username, uid, gid")

def is_expired_filepath(path, file_stat, current_time,  seconds_for_expiry):
    """
    Checks the last time a file or folder has been accessed. If it has not 
    been accessed in the days specified, then return True. False if otherwise.

    string path: The full path to the file that is being checked
    int days: The amount of days since last access that indicates that a file
        has expired. 

    output is a tuple
    output[0] = True if it is expired, false if otherwise
    output[1] = tuple containing creator info (name, uid, gid)
    output[2], output[3], output[4] return the days since the atime, 
        ctime, and mtime of the file
    """

    if os.path.islink(path):
        file_stat = os.lstat(path)
    creator = get_file_creator(path)

    # collect days since last atime, ctime, and mtime of each file 
    atime = (file_stat.st_atime) 
    ctime = (file_stat.st_ctime) 
    mtime = (file_stat.st_mtime) 
    # If all atime, ctime, mtime are more than the expiry date limit,
    # then this return true, along with the other information   \
    print(f"{current_time - atime} = {seconds_for_expiry}")
    return expiry_tuple((current_time - atime > seconds_for_expiry) and
        (current_time - ctime > seconds_for_expiry) and 
        (current_time - mtime > seconds_for_expiry), {creator}, atime, ctime, mtime)

def is_expired_link(path, file_stat, current_time, seconds_for_expiry):
    """
    Checks if a symlink is expired. Checks the link itself, along with the 
    file it points to. Returns true if both are expired. 

    Output is a tuple. 
    output[0] = True if both are expired, false if otherwise
    output[1] = tuple containing creator info (name, uid, gid)
    output[2], output[3], output[4] return the days since the atime, ctime, 
        and mtime relating to the real path that the link points to
    """
    if not os.path.islink(path):
        raise Exception("Given path is not a valid link.")
    
    # Returns true if both the link and the file it points to are expired
    real_path_information = is_expired_filepath(os.path.realpath(path), 
                                                os.stat(os.path.realpath(path)),
                                                current_time, 
                                                seconds_for_expiry)

    return expiry_tuple((is_expired_filepath(path, file_stat, seconds_for_expiry).is_expired and \
        real_path_information.is_expired), real_path_information.creator, real_path_information.atime, \
            real_path_information.ctime, real_path_information.mtime )
    

def is_expired_folder(folder_path, folder_stat, current_time, seconds_for_expiry):
    """
    Goes through all files in a folder. Returns true if ALL files in directory 
    are expire. 

    output is a tuple
    output[0] = True if it is expired, false if otherwise
    output[1] = tuple containing creator info (name, uid, gid)
    output[2], output[3], output[4] return the days to the most recent
        atime, ctime, and mtime of any file in the entire directory
    """
    file_creators = set()

    # timestamps for the folder itself 
    recent_atime = folder_stat.st_atime
    recent_ctime = folder_stat.st_atime
    recent_mtime = folder_stat.st_atime
    folder_creator = get_file_creator(folder_path)
    file_creators.add(folder_creator)
    is_expired_flag = True

    # Check if the folder itself is expired
    if not ((current_time - recent_atime > seconds_for_expiry) and
            (current_time - recent_ctime > seconds_for_expiry) and 
            (current_time - recent_mtime > seconds_for_expiry)) : is_expired_flag = False

    # Check expiry status of all files and subdirectories within the folder
    for e in Path(folder_path).rglob('*'):
        # Tracks the unique names of file creators in the directory
        file_expiry_information = is_expired(str(e), current_time, seconds_for_expiry)

        if not file_expiry_information.is_expired: 
            # First val in the expiry is always the boolean true or false
            is_expired_flag = False
        creators = file_expiry_information.creators # collects tuple of (name, uid, gid)
        # If file_expiry_information is from a folder, it should already contain a set
        # with the information of file creators
        print( file_expiry_information.ctime )
        print("AJAJAJAJAJj")
        if isinstance(creators, set):
            for user in creators:
                file_creators.add(user)
        # if file_expiry_information is from a file, and the creator is not
        # already in the set, then they're information is added. 
        else: 
            file_creators.add(creators)
        
        # update atime, ctime, mtime
        recent_atime = max(recent_atime, file_expiry_information.atime)
        recent_ctime = max(recent_atime, file_expiry_information.ctime)
        recent_mtime = max(recent_atime, file_expiry_information.mtime)
    
    
    return expiry_tuple(is_expired_flag, file_creators, recent_atime, recent_ctime, recent_mtime )


def is_expired(path, current_time, seconds_for_expiry):
    """ Interface function to return if a file-structure is expired or not. 
    TODO: Provide implementation for character device files, blocks, sockets. 
    """
    path_stat = os.stat(path)

    if stat.S_ISREG(path_stat.st_mode): # normal file
        return is_expired_filepath(path, path_stat, current_time, seconds_for_expiry)
    
    elif stat.S_ISDIR(path_stat.st_mode): # folder
        return is_expired_folder(path, path_stat, current_time, seconds_for_expiry)
    
    elif stat.S_ISLNK(path_stat.st_mode): # symlink
        return is_expired_link(path, path_stat, current_time, seconds_for_expiry)
    
    elif stat.S_ISCHR(path_stat.st_mode): # character driver
        return is_expired_filepath(path, path_stat, current_time, seconds_for_expiry)
    
    elif stat.S_ISBLK(path_stat.st_mode): # block
        return is_expired_filepath(path, path_stat, current_time, seconds_for_expiry)
    
    elif stat.S_ISFIFO(path_stat.st_mode): # pipe
        return is_expired_filepath(path, path_stat, current_time, seconds_for_expiry)



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

def notify_file_creators(file_creator_info):
    """
    TODO: implement proper notification system
    Currently is just the code to print information to a text file
    """

def scan_folder_for_expired(folder_path, current_time, seconds_for_expiry):
    """Generator function which iterates the expired top level folders
    in a given directory.
    
    Collects expiry information including:
    - all contributing users in the folder
    - the days since the most recent atime, ctime, and mtime of the entire folder
    """
    if not os.path.isdir(folder_path) :
        raise Exception("Given path directory "+ folder_path)
    for entry in os.scandir(folder_path):
        expiry_result = is_expired(entry.path, current_time, seconds_for_expiry)
        
        # path, creator tuple (name, uid, gid), atime, ctime, mtime
        print(entry.path)
        print(expiry_result.is_expired)
        yield entry.path, expiry_result.is_expired, expiry_result.creators, \
                expiry_result.atime, expiry_result.ctime, expiry_result.mtime

def collect_expired_file_information(folder_path, save_file, current_time, seconds_for_expiry):
    """
    Interface function which collects which directories are 'expired'

    String folder_path: The folder to scan for expired files
    String save_file: The jsonl file path to save the information to, ie "path_name.jsonl"
    int seconds_for_expiry: The amount of days since last usage that indicates expiry
    """
    if not os.path.isdir(folder_path):
        print("Base folder does not exist ")
        return
    
    if not save_file:
        # save_file path not given
        save_file = f"file_information_{str(datetime.datetime.fromtimestamp(current_time))}"

    path_info = dict()
    for path, is_expired, creators, atime, ctime, mtime in scan_folder_for_expired(folder_path, current_time, seconds_for_expiry):
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
                "mtime_datetime": str(datetime.datetime.fromtimestamp(mtime))
            }}        
    
    write_jsonl_information(path_info, save_file, current_time)
    return save_file 

def write_jsonl_information(dict_info, file_path, current_time):
    with open(file_path, "w") as file:
        file.write(json.dumps({"scrape_time:": current_time,
                               "scrape_time_datetime": str(datetime.datetime.fromtimestamp(current_time))}) + "\n")
        for key in dict_info:
            file.write(json.dumps(dict_info[key]) + "\n") 



def collect_creator_information(path_info_file, save_file, current_time):
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
        save_file = f"creator_information_{str(datetime.datetime.fromtimestamp(current_time))}"

    creator_info = dict()
    with open(path_info_file, "r+") as file:
        lines = file.readlines()

    for line in lines[1:]:
            # One jsonl line of path inforamtion
            path_data = json.loads(line)
            # check if the path is expired
            if path_data["expired"]:
                # take all unique creators and make a new dictionary about them
                for user in path_data["creators"]:
                    if user[1] in creator_info:
                        creator_info[user[1]]["paths"][path_data["path"]] = path_data["time_variables"]
                    else:
                        creator_info[user[1]] = {
                            "paths": {path_data["path"]: path_data["time_variables"]}, 
                            "name": user[0],
                            "uid": user[1],
                            "gid": user[2]}
        
    write_jsonl_information(creator_info, save_file, current_time)
    return save_file
