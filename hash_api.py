import hashlib
import os.path

import pyrebase
from consts import *


def calculate_hash(file_path):
    try:
        return hashlib.md5(open(file_path, 'rb').read()).hexdigest()
    except PermissionError as e:
        print(e)
        return ""


def update_hash_db(hash):
    if not os.path.exists(HASHES_FILE_NAME):
        storage = download_hash()
    else:
        firebase = pyrebase.initialize_app(fire_base_config)
        storage = firebase.storage()
    with open(HASHES_FILE_NAME, 'a') as hashes_file:
        hashes_file.write(f"\n{hash}")
    storage.child("virushashes.txt").put(HASHES_FILE_NAME)


def download_hash():
    firebase = pyrebase.initialize_app(fire_base_config)
    storage = firebase.storage()
    storage.child("virushashes.txt").download(r"D:\update_files", HASHES_FILE_NAME)
    return storage

