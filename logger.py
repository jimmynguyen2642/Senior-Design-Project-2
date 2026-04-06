import csv
import os
from config import CSV_HEADER, LOG_FILE

def init_log():
    file_exists = os.path.exists(LOG_FILE)
    if not file_exists:
        with open(LOG_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(CSV_HEADER)

def write_log_row(row):
    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(row)