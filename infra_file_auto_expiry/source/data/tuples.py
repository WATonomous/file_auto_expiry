from collections import namedtuple

expiry_tuple = namedtuple("file_tuple", "is_expired, creators, atime, ctime, mtime")
creator_tuple = namedtuple("creator_tuple", "username, uid, gid")