import pwd
import shutil
import os
import time
from pathlib import Path
import stat

def is_expired_filepath(path, days_for_expire=30):
    """
    Checks the last time a file or folder has been accessed. If it has not 
    been accessed in the days specified, then return True. False if otherwise.

    string days: The full path to the file that is being checked
    int days: The amount of days since last access that indicates that a file
        has expired. 
    """
    current_time = time.time()
    # get last access time (includes change and modification times)
    if os.path.islink(path):
        file_stat = os.lstat(path)
    else:
        file_stat = os.stat(path)
    return ((days_for_expire * 24 * 60 * 60) < (current_time - file_stat.st_atime) and
        (days_for_expire * 24 * 60 * 60) < (current_time - file_stat.st_ctime) and 
        (days_for_expire * 24 * 60 * 60) < (current_time - file_stat.st_mtime))

def is_expired_link(path, days_for_expire=30):
    """"""
    if not os.path.islink(path):
        raise Exception("Given path is not a valid link.")
    
    return is_expired_filepath(path, days_for_expire) and \
        is_expired_filepath(os.path.realpath(path), days_for_expire)
    

def is_expired_folder(folder_path, days_for_expire=30):
    """
    Goes through all files in a folder. Returns true if ALL files in directory 
    are expire. 
    """
    for e in Path(folder_path).rglob('*'):
    
        if not is_expired(str(e), days_for_expire):

            return False
    return True


def is_expired(path, days_for_expire=30):
    file_stat = os.stat(path)

    if stat.S_ISREG(file_stat.st_mode):
        return is_expired_filepath(path, days_for_expire)
    
    elif stat.S_ISDIR(file_stat.st_mode):
        return is_expired_folder(path, days_for_expire)
    
    elif stat.S_ISLNK(file_stat.st_mode):
        return is_expired_link(path, days_for_expire)
    
    elif stat.S_ISCHR(file_stat.st_mode):
        return True
    elif stat.S_ISBLK(file_stat.st_mode):
        return True
    elif stat.S_ISFIFO(file_stat.st_mode):
        return True
    elif stat.S_ISSOCK(file_stat.st_mode):
        return True 
    
    raise Exception("Given path is not a file or directory "+ path)


def get_file_creator(path):
    """
    Gets the file creators username

    ls -l filepath command on linux returns something like this:
    -rw-rw-r-- 1 machung machung 4 Feb 17 05:14 /home/machung/test.txt
    So we select the file owner username from this command output. 

    string file_path: The absolute path of the file
    """
    # Get the UID of the file or directory owner
    # Get the username associated with the UID
    try:
        username = pwd.getpwuid(os.stat(path).st_uid).pw_name
    except KeyError:
        """ FIX THIS LATER"""
        return f"user{os.stat(path).st_uid}"
    return username

def notify_file_creator(file_creator, path):
    """
    TODO: implement proper notification system
    """
    print(file_creator + ": " + (path))
    #with open("", "a+") as file:
    #    file.write(file_creator + ": " + (path) + "\n")
    

def scan_folder_for_expired(folder_path, days_for_expire=30):
    for entry in os.scandir(folder_path):
        if is_expired(entry.path, days_for_expire) :
            yield entry.path 

def delete_expired_files(folder_path, temp_folder, days_for_expire=30):
    if  not os.path.isdir(folder_path) or not os.path.isdir(temp_folder):
        print("Base folder does not exist ")
        return
    
    for path in scan_folder_for_expired(folder_path, days_for_expire):
        notify_file_creator(get_file_creator(path), path)
        #shutil.move(path, temp_folder)
    
    #shutil.rmtree(temp_folder)
    