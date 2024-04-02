import pwd
import shutil
import os
import sys
import time
from pathlib import Path
import stat

def is_expired_filepath(path, days_for_expire=30):
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
    current_time = time.time()

    if os.path.islink(path):
        file_stat = os.lstat(path)
    else:
        file_stat = os.stat(path)
    creator = get_file_creator(path)

    # collect days since last atime, ctime, and mtime of each file 
    atime = (current_time - (file_stat.st_atime)) / 3600 / 24
    ctime = (current_time - (file_stat.st_ctime)) / 3600 / 24
    mtime = (current_time - (file_stat.st_mtime)) / 3600 / 24

    # If all atime, ctime, mtime are more than the expiry date limit,
    # then this return true, along with the other information
    return ((days_for_expire) < (atime) and
        (days_for_expire ) < (ctime) and 
        (days_for_expire) < (mtime)), {creator}, atime, ctime, mtime

def is_expired_link(path, days_for_expire=30):
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
    real_path_information = is_expired_filepath(os.path.realpath(path), days_for_expire)

    return (is_expired_filepath(path, days_for_expire)[0] and \
        real_path_information[0]), real_path_information [1], real_path_information [2], \
            real_path_information [3], real_path_information [4], 
    

def is_expired_folder(folder_path, days_for_expire=30):
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
    for e in Path(folder_path).rglob('*'):
        # Tracks the unique names of file creators in the directory
        file_expiry_information = is_expired(str(e), days_for_expire)

        if not file_expiry_information[0]: 
            # First val in the expiry is always the boolean true or false
            return False, file_creators, recent_atime, recent_ctime, recent_mtime 
        
        creator = file_expiry_information[1] # collects tuple of (name, uid, gid)

        # If file_expiry_information is from a folder, it should already contain a set
        # with the information of file creators
        if isinstance(creator, set):
            for user in creator:
                if user not in file_creators:
                    #Adds entire creator tuple
                    file_creators.add(user)
        # if file_expiry_information is from a file, and the creator is not
        # already in the set, then they're information is added. 
        else: 
            if creator not in file_creators:
                #Adds entire creator tuple
                file_creators.add(creator)
        
        # update atime, ctime, mtime
        recent_atime = min(recent_atime, file_expiry_information[2])
        recent_ctime = min(recent_atime, file_expiry_information[3])
        recent_mtime = min(recent_atime, file_expiry_information[4])

    return True, file_creators, recent_atime, recent_ctime, recent_mtime 


def is_expired(path, days_for_expire=30):
    """ Interface function to return if a file-structure is expired or not. 
    TODO: Provide implementation for character device files, blocks, sockets. 
    """
    file_stat = os.stat(path)

    if stat.S_ISREG(file_stat.st_mode): # normal file
        return is_expired_filepath(path, days_for_expire)
    
    elif stat.S_ISDIR(file_stat.st_mode): # folder
        return is_expired_folder(path, days_for_expire)
    
    elif stat.S_ISLNK(file_stat.st_mode): # symlink
        return is_expired_link(path, days_for_expire)
    
    elif stat.S_ISCHR(file_stat.st_mode): # character driver
        return is_expired_filepath(path, days_for_expire)
    
    elif stat.S_ISBLK(file_stat.st_mode): # block
        return is_expired_filepath(path, days_for_expire)
    
    elif stat.S_ISFIFO(file_stat.st_mode): # pipe
        return is_expired_filepath(path, days_for_expire)



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
    return username, os.stat(path).st_uid, os.stat(path).st_gid

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


def scan_folder_for_expired(folder_path, days_for_expire=30):
    """Generator function which iterates the expired top level folders
    in a given directory.
    
    Collects expiry information including:
    - all contributing users in the folder
    - the days since the most recent atime, ctime, and mtime of the entire folder
    """
    if not os.path.isdir(folder_path) :
        raise Exception("Given path directory "+ folder_path)
    for entry in os.scandir(folder_path):
        expiry_result = is_expired(entry.path, days_for_expire)
        
            # path, creator tuple (name, uid, gid), atime, ctime, mtime
        yield entry.path, expiry_result[0], expiry_result[1], expiry_result[2], expiry_result[3],  \
            expiry_result[4]

def collect_expired_file_information(folder_path, days_for_expire=30):
    """
    Interface function which collects which directories are 'expired'

    String folder_path: The folder to scan for expired files
    int days_for_expiry: The amount of days since last usage that indicates expiry
    """
    if  not os.path.isdir(folder_path):
        print("Base folder does not exist ")
        return
    path_info = dict()
    for path, is_expired, creators, atime, ctime, mtime in scan_folder_for_expired(folder_path, days_for_expire):
        # handles generating the dictionary
        path_info[path] = {
            "creators": [creator for creator in creators],
            "expired": is_expired,
            "timestamps": [atime, ctime, mtime]
        }
        
    return path_info

def collect_creator_information(path_info):
    """
    Returns a dictionary relating path information to each creator
    Must be given the return value of form similar to the output of 
    collect_expired_file_information()
    """
    creator_info = dict()
    for path in path_info:
        if path_info[path]["expired"]:
            for user in path_info[path]["creators"]:
                if user[1] in creator_info:
                    creator_info[user[1]]["paths"][path] = path_info[path]["timestamps"]

                else:
                    creator_info[user[1]] = {"paths": {path: path_info[path]["timestamps"]}, 
                                                "name": user[0],
                                                "gid": user[2]}

    return creator_info
