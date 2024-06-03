# Network constants
MASK_BYTE_ON = "255"
MAC_LENGTH = 6
PORT_DST = 8889
ARP_DLL_PATH = r"D:\ARP_send.dll"
PROCESS_CHECK_PATH = r"D:\Process_dll.dll"
BUFFER_SIZE = 1024

# Database constants
DB_NAME = "addresses.db"
INSERT_SQL_QUERY = '''INSERT INTO computers(ip, mac, is_on) VALUES(?, ?, ?)'''
UPDATE_ROW_QUERY = '''UPDATE computers SET is_on=? WHERE ROWID=?'''
GET_DATA_SQL_QUERY = '''SELECT * FROM computers'''

# firebase
fire_base_config = {
    "apiKey": "AIzaSyDG9h4RsPHAjHEnJ4ytBuP8gxBpdxJ1TbI",
    "authDomain": "virus-hashes.firebaseapp.com",
    "projectId": "virus-hashes",
    "storageBucket": "virus-hashes.appspot.com",
    "messagingSenderId": "859811211895",
    "appId": "1:859811211895:web:2439b142759066f2e2b472",
    "measurementId": "G-MXJ1TWB808",
    "databaseURL": "gs://virus-hashes.appspot.com/virushashes.txt"
}

# hash
HASHES_FILE_NAME = "hash.txt"
MD5_NULL_HASH = "d41d8cd98f00b204e9800998ecf8427e"

# GUI constants
X_DRAW_START = 100
Y_DRAW_START = 130

# ENCRYPTION CONSTANTS
BLOCK_SIZE = 16
PAD = b'\x00'

# PROTOCOL CONSTS
LENGTH_FIELD_SIZE = 8

# REAL TIME MONITORING
RTM_PATH = "rtm.exe"
QUARANTINE_PATH = "Quarantine"
