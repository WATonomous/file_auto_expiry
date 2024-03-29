# infra_file_auto_expiry

Relating to issue: https://github.com/WATonomous/infra-config/issues/1143

This project is meant to help automatically expire and delete files. It's currently at the stage of gathering all necessary information about file deletion easier. In the future, it is required to add a notification system for users whose files are to be deleted, and an actual deletion system. C

Currently it moves through every single top level folder in a directory, and checks whether it is expired or not. This means that every single file in that directory tree must be expired. As it does this, it gathers all the users who created files in that directory, and the days since the most RECENT atime, ctime, and mtime of ANY file in that directory. It only collects these for folders which have been confirmed to be expired.

This is placed into a dictionary similar to below:

    all_creators: {
        uid1: {
            "name": "username1"    
            "gid": usergid
            "paths":{
                "path1": [atime, ctime, mtime],
                "path2": [atime, ctime, mtime],
                "path3": [atime, ctime, mtime],
            }
        }
        uid2: {
            "name": "username2"    
            "gid": usergid
            "paths":{
                "path1": [atime, ctime, mtime]
            }
        }
    }


This can be used by falling the file_expiry.sh bash script. Currently, it will not actually have an output, but you may see the output by modifying the "notify_file_creators" function and adding the name of a text file into that block. 
