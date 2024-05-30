import ctypes
import socket
import struct
import subprocess
from consts import *


class Node(ctypes.Structure):
    _fields_ = [('ip', ctypes.c_ulong),  # use correct types
                ('mac', ctypes.c_ubyte * MAC_LENGTH),
                ('status', ctypes.c_bool)]


def get_network_mask(ip):
    proc = subprocess.Popen('ipconfig', stdout=subprocess.PIPE)

    while True:
        line = proc.stdout.readline()
        if ip.encode() in line:
            break
    mask = proc.stdout.readline().rstrip().split(b':')[-1].replace(b' ', b'').decode()
    return mask


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    return ip


def get_start_ip(ip, mask):
    iplist = ip.split(".")
    masklist = mask.split(".")
    iplist = [int(i) if masklist[iplist.index(i)] == MASK_BYTE_ON else 0 for i in iplist]
    return iplist


def get_end_ip(ip, mask):
    iplist = ip.split(".")
    masklist = mask.split(".")
    iplist = [int(i) if masklist[iplist.index(i)] == "255" else 255 for i in iplist]
    return iplist


def get_addresses_dict():
    ip = get_ip()
    mask = get_network_mask(ip)
    masklist = mask.split(".")

    start_ip = get_start_ip(ip, mask)
    end_ip = get_end_ip(ip, mask)

    start_arr = (ctypes.c_int * len(start_ip))(*start_ip)
    end_arr = (ctypes.c_int * len(end_ip))(*end_ip)
    addresses = {}

    lib = ctypes.CDLL(ARP_DLL_PATH)
    lib.get_addr.argtypes = [ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int)]
    lib.get_addr.restype = ctypes.POINTER(Node)

    res = lib.get_addr(start_arr, end_arr)

    for i in range(255 ** masklist.count("0")):
        if res[i].status:
            ip = res[i].ip
            final_ip = socket.inet_ntoa(struct.pack('L', ip))
            mac_addr = ":".join([hex(j)[2:] for j in res[i].mac])
            addresses[final_ip] = mac_addr
    return addresses


