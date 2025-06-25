import argparse
import shutil
import time

# EndNote database file path
ENL_FILE_PATH = None
# EndNote data folder path
DATA_FOLDER_PATH = None
# Log switch
ENABLE_LOG = False
# Use backup switch
USE_BACKUP = False

def parse_args():
    global ENL_FILE_PATH, DATA_FOLDER_PATH, ENABLE_LOG, USE_BACKUP
    parser = argparse.ArgumentParser(description="EndNote MCP Service configuration")
    parser.add_argument('--enl-file', '-e', required=True, help='Path to the EndNote .enl file')
    parser.add_argument('--data-folder', '-d', required=True, help='Path to the EndNote .Data folder')
    parser.add_argument('--enable-log', '-l', action='store_true', help='Enable detailed log output (default: False)')
    parser.add_argument('--use-backup', '-b', action='store_true', help='Use .enl.backup file for all DB operations (default: False)')
    args = parser.parse_args()
    ENABLE_LOG = args.enable_log
    USE_BACKUP = args.use_backup
    if USE_BACKUP:
        ENL_FILE_PATH = args.enl_file + ".backup"
        # Automatically refresh backup on startup
        try:
            shutil.copy2(args.enl_file, ENL_FILE_PATH)
            if ENABLE_LOG:
                print(f"[CONFIG] .enl.backup refreshed at {time.strftime('%Y-%m-%d %H:%M:%S')}")
        except Exception as e:
            if ENABLE_LOG:
                print(f"[CONFIG] Failed to refresh .enl.backup: {e}")
    else:
        ENL_FILE_PATH = args.enl_file
    DATA_FOLDER_PATH = args.data_folder
    if ENABLE_LOG:
        print(f"[CONFIG] ENL_FILE_PATH: {ENL_FILE_PATH}")
        print(f"[CONFIG] DATA_FOLDER_PATH: {DATA_FOLDER_PATH}")
        print(f"[CONFIG] ENABLE_LOG: {ENABLE_LOG}")
        print(f"[CONFIG] USE_BACKUP: {USE_BACKUP}")
