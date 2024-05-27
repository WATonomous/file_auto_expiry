import os
import stat
from data.expiry_constants import *
from data.expiry_constants import KNOWN_DIRECTORIES
from data.tuples import *
from utils.file_creator import *

def is_expired(path, scrape_time, seconds_for_expiry):
    """ Interface function to return if a file-structure is expired or not. 
    TODO: Provide implementation for character device files, blocks, sockets. 
    """
    
    path_stat = os.stat(path)
    if stat.S_ISREG(path_stat.st_mode): # normal file
        return is_expired_filepath(path, path_stat, scrape_time, seconds_for_expiry)
    
    elif stat.S_ISDIR(path_stat.st_mode): # folder
        return is_expired_folder(path, path_stat, scrape_time, seconds_for_expiry)
    
    elif stat.S_ISLNK(path_stat.st_mode): # symlink
        return is_expired_link(path, path_stat, scrape_time, seconds_for_expiry)
    
    elif stat.S_ISCHR(path_stat.st_mode): # character driver
        return is_expired_filepath(path, path_stat, scrape_time, seconds_for_expiry)
    
    elif stat.S_ISBLK(path_stat.st_mode): # block
        return is_expired_filepath(path, path_stat, scrape_time, seconds_for_expiry)
    
    elif stat.S_ISFIFO(path_stat.st_mode): # pipe
        return is_expired_filepath(path, path_stat, scrape_time, seconds_for_expiry)
    
    elif stat.S_ISSOCK(path_stat.st_mode): # socket
        return is_expired_filepath(path, path_stat, scrape_time, seconds_for_expiry)


def is_expired_filepath(path, file_stat, scrape_time,  seconds_for_expiry):
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
    # then this return true, along with the other information  
    return expiry_tuple(check_time_stamps(atime, ctime, mtime, scrape_time, seconds_for_expiry),
                         {creator}, atime, ctime, mtime)

def check_time_stamps(atime, ctime, mtime, scrape_time, seconds_for_expiry):
    """
    Checks if all atime, ctime, and mtime are expired. 
    Returns True when all are expired. 
    """
    return ((scrape_time - atime > seconds_for_expiry) and 
            (scrape_time - ctime > seconds_for_expiry) and 
            (scrape_time - mtime > seconds_for_expiry))

def is_expired_link(path, file_stat, scrape_time, seconds_for_expiry):
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

    
    #TODO: implement edge case for when the link points to a recursive directory
    # For now, just handle by only considering the link itself
    return is_expired_filepath(path, file_stat, scrape_time, 
                                                seconds_for_expiry)
    

def is_expired_folder(folder_path, folder_stat, scrape_time, seconds_for_expiry):
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
    recent_ctime = folder_stat.st_ctime
    recent_mtime = folder_stat.st_mtime
    folder_creator = get_file_creator(folder_path)
    file_creators.add(folder_creator)
    is_expired_flag = check_time_stamps(recent_atime, recent_ctime, recent_mtime, 
                              scrape_time, seconds_for_expiry)

    if check_folder_if_known(path=folder_path):
        return expiry_tuple(is_expired_flag, file_creators, recent_atime, recent_ctime, recent_mtime )
    # Check expiry status of all files and subdirectories within the folder
    for member_file_name in os.listdir(folder_path):
        # Tracks the unique names of file creators in the directory
        member_file_path = os.path.join(folder_path, member_file_name)

        if not os.path.exists(member_file_path) or os.path.islink(member_file_path):
            continue

        file_expiry_information = is_expired(str(member_file_path), scrape_time, seconds_for_expiry)

        if file_expiry_information.is_expired: 
            # First val in the expiry is always the boolean true or false
            is_expired_flag = False

        creators = file_expiry_information.creators # collects tuple of (name, uid, gid)
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
        recent_atime = max(recent_atime, file_expiry_information.atime)
        recent_ctime = max(recent_ctime, file_expiry_information.ctime)
        recent_mtime = max(recent_mtime, file_expiry_information.mtime)
    
    return expiry_tuple(is_expired_flag, file_creators, recent_atime, recent_ctime, recent_mtime )

def check_folder_if_known(path):
    """
    Checks if a folder path is within a known set of directories
    that are large and typically non-edited by users. 
    """
    base_name = os.path.basename(path)
    parent_path_name = os.path.basename(os.path.dirname(path))
    if f"{parent_path_name}/{base_name}" in KNOWN_DIRECTORIES:
        return True
    
def catch_link_issues(path):
    """
    Returns True if a link leads to a link or a directory
    """
    if os.path.islink(path):
        real_path = os.path.realpath(path)
        if os.path.islink(real_path) or os.path.isdir(real_path):
            return True