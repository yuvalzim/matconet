import psutil
import os
from consts import *


def get_disk_names():
    disk_names = set()
    for partition in psutil.disk_partitions(all=True):
        disk_names.add(partition.device)
    return list(disk_names)


def create_quarantine_folder():
    if not os.path.exists(QUARANTINE_PATH):
        os.mkdir(QUARANTINE_PATH)


def get_quarantined_files():
    files = os.listdir(QUARANTINE_PATH)
    return files


def delete_file(path):
    os.remove(path)
