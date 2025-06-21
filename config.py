import os
import argparse

# EndNote database file path
ENL_FILE_PATH = None
# EndNote data folder path
DATA_FOLDER_PATH = None
# Log switch
ENABLE_LOG = False

def parse_args():
    global ENL_FILE_PATH, DATA_FOLDER_PATH, ENABLE_LOG
    parser = argparse.ArgumentParser(description="EndNote MCP Service configuration")
    parser.add_argument('--enl-file', '-e', required=True, help='Path to the EndNote .enl file')
    parser.add_argument('--data-folder', '-d', required=True, help='Path to the EndNote .Data folder')
    parser.add_argument('--enable-log', '-l', action='store_true', help='Enable detailed log output (default: False)')
    args = parser.parse_args()
    ENL_FILE_PATH = args.enl_file
    DATA_FOLDER_PATH = args.data_folder
    ENABLE_LOG = args.enable_log
    if ENABLE_LOG:
        print(f"[CONFIG] ENL_FILE_PATH: {ENL_FILE_PATH}")
        print(f"[CONFIG] DATA_FOLDER_PATH: {DATA_FOLDER_PATH}")
        print(f"[CONFIG] ENABLE_LOG: {ENABLE_LOG}")
