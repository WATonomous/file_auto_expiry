import pwd
import shutil
import os
import time

def is_expired_file(path, days_for_expire=30):
    """
    Checks the last time a file or folder has been accessed. If it has not 
    been accessed in the days specified, then return True. False if otherwise.

    string days: The full path to the file that is being checked
    int days: The amount of days since last access that indicates that a file
        has expired. 
    """
    current_time = time.time()
    # get last access time (includes change and modification times)
    file_stat = os.stat(path)

    # compare days for expiry (in seconds) to the time since last access
    return ((days_for_expire * 24 * 60 * 60) < (current_time - file_stat.st_atime) and
        (days_for_expire * 24 * 60 * 60) < (current_time - file_stat.st_ctime) and 
        (days_for_expire * 24 * 60 * 60) < (current_time - file_stat.st_mtime))

def is_expired_folder(folder_path, days_for_expire=30):
    """
    Goes through all files in a folder, and deletes the ones that
    have expired

    string base_folder: The folder containing the files to delete
    """
    if not os.path.isdir(folder_path):
        print("Bad folder path:", folder_path)
        return False
    
    all_files_expired = True
    for entry in os.scandir(folder_path):
        if entry.is_dir():
            if not is_expired_folder(entry.path, days_for_expire):
                return False
        elif entry.is_file() and not is_expired(entry.path, days_for_expire):
            all_files_expired = False
    return all_files_expired

def is_expired(path, days_for_expire=30):
    if os.path.isfile(path):
        return is_expired_file(path, days_for_expire)
    if os.path.isdir(path):
        return is_expired_folder(path, days_for_expire)
    
    return False

def get_file_creator(path):
    """
    Gets the file creators username

    ls -l filepath command on linux returns something like this:
    -rw-rw-r-- 1 machung machung 4 Feb 17 05:14 /home/machung/test.txt
    So we select the file owner username from this command output. 

    string file_path: The absolute path of the file
    """
    try:
        # Get the UID of the file or directory owner
        uid = os.stat(path).st_uid
        # Get the username associated with the UID
        username = pwd.getpwuid(uid).pw_name
        return username
    except FileNotFoundError:
        print(f"Error: File '{path}' not found.")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def notify_file_creator(file_creator):
    """
    TODO: implement proper notification system
    """
    print(f"Deleting file by ", file_creator)

def scan_folder_for_expired(folder_path, days_for_expire=30):
    for entry in os.scandir(folder_path):
        if is_expired(entry.path, days_for_expire):
            yield entry.path 

def delete_expired_files(folder_path, temp_folder, days_for_expire=30):
    if not os.path.isdir(folder_path) or not os.path.isdir(temp_folder):
        print("Base folder does not exist ")
        return
    
    for path in scan_folder_for_expired(folder_path, days_for_expire):
        notify_file_creator(get_file_creator(path))
        shutil.move(path, temp_folder)
    
    shutil.rmtree(temp_folder)
    