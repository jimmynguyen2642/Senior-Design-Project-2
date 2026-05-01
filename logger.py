import csv
import os
import shutil
from datetime import datetime
from config import CSV_HEADER, LOG_FILE

ARCHIVE_DIR = "/mnt/sdcard/logs"

def init_log():
    # Archive old log to SD card if it exists
    if os.path.exists(LOG_FILE):
        try:
            os.makedirs(ARCHIVE_DIR, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_path = os.path.join(ARCHIVE_DIR, f"sensor_log_{timestamp}.csv")
            shutil.copy2(LOG_FILE, archive_path)
            print(f"Archived old log to {archive_path}", flush=True)
        except Exception as e:
            print(f"Could not archive log: {e}", flush=True)

    # Start fresh log
    with open(LOG_FILE, "w", newline="") as f:
        csv.writer(f).writerow(CSV_HEADER)

def write_log_row(row):
    with open(LOG_FILE, "a", newline="") as f:
        csv.writer(f).writerow(row)