import subprocess
import shutil
import os
import datetime
import time
import random
import string

def generate_folder(base_path, permission=700):
    """
    Generates a new folder with the specified permissions

    string base_path: parent folder to generate the new folder
    int permission: The permission code for the folder. Default is 700,
        meaning that the folder is accessible by root only
    """
    # Generate folder name
    folder_name = "wa"#datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S')
    folder_path = os.path.join(base_path, folder_name)

    # Re run above code until it is confirmed we have a new folder
    while os.path.isdir(folder_path):
        folder_name = datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S')
        unique_random_key = "".join(random.choices(string.ascii_letters + string.digits, k=5))
        folder_path = os.path.join(base_path, f"{folder_name}{unique_random_key}")
    
    # generate folder
    os.makedirs(folder_path)
    
    # modify folder settings permissions
    try:
        subprocess.run(["sudo", "chmod", str(permission), folder_path], check=True)
    except Exception as e:
        # Catch for errors, likely from non existing permission code
        print(e)
        os.rmdir(folder_path)
        return None

    return folder_path

def is_expired_file(file_path, days_for_expire=30):
    """
    Checks the last time a file has been accessed. If it has not been accessed 
    in the days specified, then return True. False if otherwise.

    string days: The full path to the file that is being checked
    int days: The amount of days since last access that indicates that a file
        has expired. 
    """
    current_time = time.time()

    # get last access time (includes change and modification times)
    file_stat = os.stat(file_path)
    last_access = file_stat.st_atime

    # Generate amount of time since last access
    seconds_last_access = (current_time - last_access) 

    # compare days for expiry (in seconds) to the time since last access
    return (days_for_expire * 24 * 60 * 60) < seconds_last_access

def get_file_creator(file_path):
    """
    Gets the file creators username

    ls -l filepath command on linux returns something like this:
    -rw-rw-r-- 1 machung machung 4 Feb 17 05:14 /home/machung/test.txt
    So we select the file owner username from this command output. 

    string file_path: The absolute path of the file
    """
    sub_result = subprocess.run(["ls", "-l", file_path], capture_output=True)
    print(sub_result.stderr)
    if not sub_result.stderr:
        file_owner = sub_result.stdout.decode().split()[2]
        return file_owner
    return None

def notify_file_creator(file_creator):
    """
    TODO: implement proper notification system
    """
    print(f"Deleting file by ", file_creator)

def delete_expired_files(base_folder):
    """
    Goes through all files in a folder, and deletes the ones that
    have expired

    string base_folder: The folder containing the files to delete
    """

    temp_folder = generate_folder(os.path.dirname(base_folder))
    if temp_folder is None:
        print("Unable to create a temporary folder, cancelling file deletion")
        return

    for dir_path, dir_names, filenames in os.walk(base_folder):
        for filename in filenames:
            # get full path for a specific file
            file_path = os.path.join(dir_path, filename)
            if is_expired_file(file_path):
                notify_file_creator(get_file_creator(file_path))

                # update filename in case there are files with 
                # the same name that need to be deleted
                file_path_no_extension, extension = os.path.splitext(file_path)
                unique_timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H%M%S')
                unique_random_key = "".join(random.choices(string.ascii_letters + string.digits, k=5))
                file_path_unique = f"{file_path_no_extension}_{unique_timestamp}_{unique_random_key}{extension}"
                
                os.rename(file_path, file_path_unique)
                shutil.move(file_path_unique, temp_folder)

                # If directory is empty now, just delete the directory
                if len(os.listdir(dir_path)) == 0 and dir_path is not base_folder:
                    os.rmdir(dir_path)

    shutil.rmtree(temp_folder)
    