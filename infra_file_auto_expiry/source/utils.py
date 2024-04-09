import pwd
import shutil
import os
import sys
import time
from pathlib import Path
import stat
import json
from collections import namedtuple

expiry_tuple = namedtuple("file_tuple", "is_expired, creators, atime, ctime, mtime")
creator_tuple = namedtuple("creator_tuple", "username, uid, gid")

def is_expired_filepath(path, file_stat, current_time,  days_for_expire):
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
    else:
        file_stat = os.stat(path)
    creator = get_file_creator(path)

    # collect days since last atime, ctime, and mtime of each file 
    atime = (current_time - (file_stat.st_atime)) 
    ctime = (current_time - (file_stat.st_ctime)) 
    mtime = (current_time - (file_stat.st_mtime)) 
    with open("/home/machung/infra_file_auto_expiry/infra_file_auto_expiry/source/gen.txt", "a") as file:
        file.write(f"{atime} {days_for_expire} \n")
    # If all atime, ctime, mtime are more than the expiry date limit,
    # then this return true, along with the other information   \

    return expiry_tuple(((days_for_expire) < (atime) and
        (days_for_expire ) < (ctime) and 
        (days_for_expire) < (mtime)), {creator}, atime, ctime, mtime)

def is_expired_link(path, file_stat, current_time, days_for_expire):
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
                                                days_for_expire)

    return expiry_tuple((is_expired_filepath(path, file_stat, days_for_expire).is_expired and \
        real_path_information.is_expired), real_path_information.creator, real_path_information.atime, \
            real_path_information.ctime, real_path_information.mtime )
    

def is_expired_folder(folder_path, current_time, days_for_expire):
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
    recent_atime = sys.maxsize
    recent_ctime = sys.maxsize
    recent_mtime = sys.maxsize
    folder_creator = get_file_creator(folder_path)
    file_creators.add(folder_creator)
    for e in Path(folder_path).rglob('*'):
        # Tracks the unique names of file creators in the directory
        component_expiry_information = is_expired(str(e), current_time, days_for_expire)

        if not component_expiry_information.is_expired: 
            # First val in the expiry is always the boolean true or false
            return expiry_tuple(False, file_creators, recent_atime, recent_ctime, recent_mtime 
        )
        creators = component_expiry_information.creators # collects tuple of (name, uid, gid)
        # If file_expiry_information is from a folder, it should already contain a set
        # with the information of file creators
    
        if isinstance(creators, set):
            for user in creators:
                file_creators.add(user)
        # if file_expiry_information is from a file, and the creator is not
        # already in the set, then they're information is added. 
        else: 
            file_creators.add(creators)
        
        # update atime, ctime, mtime
        recent_atime = min(recent_atime, component_expiry_information.atime)
        recent_ctime = min(recent_atime, component_expiry_information.ctime)
        recent_mtime = min(recent_atime, component_expiry_information.mtime)
    with open("/home/machung/infra_file_auto_expiry/infra_file_auto_expiry/source/gen.txt", "a") as file:
        file.write(f"{file_creators} \n")
    return expiry_tuple(True, file_creators, recent_atime, recent_ctime, recent_mtime )


def is_expired(path, current_time, days_for_expire):
    """ Interface function to return if a file-structure is expired or not. 
    TODO: Provide implementation for character device files, blocks, sockets. 
    """
    file_stat = os.stat(path)

    if stat.S_ISREG(file_stat.st_mode): # normal file
        return is_expired_filepath(path, file_stat, current_time, days_for_expire)
    
    elif stat.S_ISDIR(file_stat.st_mode): # folder
        return is_expired_folder(path, current_time, days_for_expire)
    
    elif stat.S_ISLNK(file_stat.st_mode): # symlink
        return is_expired_link(path, file_stat, current_time, days_for_expire)
    
    elif stat.S_ISCHR(file_stat.st_mode): # character driver
        return is_expired_filepath(path, file_stat, current_time, days_for_expire)
    
    elif stat.S_ISBLK(file_stat.st_mode): # block
        return is_expired_filepath(path, file_stat, current_time, days_for_expire)
    
    elif stat.S_ISFIFO(file_stat.st_mode): # pipe
        return is_expired_filepath(path, file_stat, current_time, days_for_expire)



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
    # for user in file_creator_info:
    #     with open("", "a+") as file:
    #         #file.write(f"{user_information[user]}\n")
    #         file.write(f"File creator: {file_creator_info[user]['name']} : {user}\n")
    #         for path, timestamps in file_creator_info[user]["paths"].items():
    #             file.write(f"path: {path}\n")
    #             file.write(f"   atime: {timestamps[0]}\n")
    #             file.write(f"   ctime: {timestamps[1]}\n")
    #             file.write(f"   mtime: {timestamps[2]}\n\n")


def scan_folder_for_expired(folder_path, current_time, days_for_expire):
    """Generator function which iterates the expired top level folders
    in a given directory.
    
    Collects expiry information including:
    - all contributing users in the folder
    - the days since the most recent atime, ctime, and mtime of the entire folder
    """
    if not os.path.isdir(folder_path) :
        raise Exception("Given path directory "+ folder_path)
    for entry in os.scandir(folder_path):
        expiry_result = is_expired(entry.path, current_time, days_for_expire)

        # get current folders creator just in case it's empty
        expiry_result.creators.add(get_file_creator(entry))
            # path, creator tuple (name, uid, gid), atime, ctime, mtime
        yield entry.path, expiry_result.is_expired, expiry_result.creators, \
            expiry_result.atime, expiry_result.ctime, expiry_result.mtime

def collect_expired_file_information(folder_path, current_time, days_for_expire):
    """
    Interface function which collects which directories are 'expired'

    String folder_path: The folder to scan for expired files
    int days_for_expiry: The amount of days since last usage that indicates expiry
    """
    if  not os.path.isdir(folder_path):
        print("Base folder does not exist ")
        return
    path_info = dict()
    for path, is_expired, creators, atime, ctime, mtime in scan_folder_for_expired(folder_path, current_time, days_for_expire):
        # handles generating the dictionary
        path_info[path] = { 
            "path": path, # storing pathname so we keep it when we transfer the dictionary to jsonl
            "creators": [creator for creator in creators],
            "expired": is_expired,
            "atime": atime,
            "ctime": ctime,
            "mtime": mtime
        }
    
    write_jsonl_information(path_info, "infra_file_auto_expiry/source/data/file_information.jsonl")

    return path_info # infra_file_auto_expiry/source/data/file_information.jsonl

def write_jsonl_information(dict_info, file_path):
    with open (file_path, "w") as file:
        for key in dict_info:
            file.write(json.dumps(dict_info[key]) + "\n") 



def collect_creator_information(folder_path, current_time, seconds_for_expire, replace_file_information = False):
    """
    Returns a dictionary relating path information to each creator
    Must be given the return value of form similar to the output of 
    collect_expired_file_information()
    """
    if not os.path.exists("infra_file_auto_expiry/source/data/file_information.jsonl") or \
            replace_file_information:
        collect_expired_file_information(folder_path, current_time, seconds_for_expire)

    creator_info = dict()
    with open("infra_file_auto_expiry/source/data/file_information.jsonl", "r+") as file:
        for line in file:
            # One jsonl line of path inforamtion
            path_data = json.loads(line)
            # check if the path is expired
            if path_data["expired"]:
                # take all unique creators and make a new dictionary about them
                for user in path_data["creators"]:
                    if user[1] in creator_info:
                        creator_info[user[1]]["paths"][path_data["path"]] = {
                            
                            "atime": path_data["atime"],
                            "ctime": path_data["ctime"],
                            "mtime": path_data["mtime"]
                        }

                        
                    else:
                        creator_info[user[1]] = {"paths": {path_data["path"]: {
                            "atime": path_data["atime"],
                            "ctime": path_data["ctime"],
                            "mtime": path_data["mtime"]

                        }}, 
                                                    "name": user[0],
                                                    "uid": user[1],
                                                    "gid": user[2]}
        
    write_jsonl_information(creator_info, "infra_file_auto_expiry/source/data/creator_information.jsonl")
    #rint(creator_info)
    return creator_info
