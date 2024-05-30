import ctypes
import sys
import enable_py_privs
import faulthandler
from consts import *


class Proc(ctypes.Structure):
    _fields_ = [('name', ctypes.c_char_p),  # use correct types
                ('id', ctypes.c_int)]


class ListProc(ctypes.Structure):
    _fields_ = [('procs', ctypes.POINTER(Proc)),  # use correct types
                ('countP', ctypes.c_int)]


def get_proc_dict():
    enable_py_privs.enable_privs()
    faulthandler.enable()
    proc_dict = {}
    lib = ctypes.CDLL(PROCESS_CHECK_PATH)

    lib.getProcData.restype = ctypes.POINTER(ListProc)
    try:
        list_proc = lib.getProcData()
        res = list_proc[0].procs
        p_count = list_proc[0].countP
        for i in range(p_count):
            if res[i].name:
                proc_dict[res[i].name.decode()] = res[i].id
    except BaseException as e:
        print(e)
    return proc_dict


def disable_privs(pid):
    lib = ctypes.CDLL(PROCESS_CHECK_PATH)
    lib.DisableAllPrivs.restypes = ctypes.c_int
    lib.DisableAllPrivs(pid)


def close_proc(pid):
    lib = ctypes.CDLL(PROCESS_CHECK_PATH)
    lib.closeProc.restypes = ctypes.c_int
    lib.closeProc(pid)



