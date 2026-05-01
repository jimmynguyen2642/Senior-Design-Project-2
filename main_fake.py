import time
import csv
import os
import serial
import random
from datetime import datetime

# ── Config ──
LOG_FILE   = "/home/admin/Senior-Design-Project-2/sensor_log_fake.csv"
RADIO_PORT = "/dev/serial0"
RADIO_BAUD = 9600

CSV_HEADER = [
    "timestamp","latitude","longitude","elevation","satellites",
    "ang_vel_x","ang_vel_y","ang_vel_z",
    "accel_x","accel_y","accel_z",
    "mag_x","mag_y","mag_z"
]

def mock_row():
    return [
        datetime.now().isoformat(),
        36.1384 + random.uniform(-0.0001, 0.0001),
        -97.0667 + random.uniform(-0.0001, 0.0001),
        285.0 + random.uniform(-1, 1),
        random.randint(4, 9),
        random.uniform(-0.01, 0.01),
        random.uniform(-0.01, 0.01),
        random.uniform(-0.01, 0.01),
        random.uniform(-0.1, 0.1),
        random.uniform(-0.1, 0.1),
        9.81 + random.uniform(-0.1, 0.1),
        random.uniform(10, 20),
        random.uniform(-5, 5),
        random.uniform(-130, -120),
    ]

def init_log():
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", newline="") as f:
            csv.writer(f).writerow(CSV_HEADER)

def write_log(row):
    with open(LOG_FILE, "a", newline="") as f:
        csv.writer(f).writerow(row)

def init_serial(port, baud):
    try:
        return serial.Serial(port, baud, timeout=1)
    except Exception as e:
        print(f"Could not open {port}: {e}")
        return None

def send(ser, line):
    if ser is None:
        return
    try:
        ser.write((line + "\n").encode("utf-8"))
        ser.flush()
    except Exception as e:
        print(f"Send error: {e}")

def main():
    init_log()
    radio = init_serial(RADIO_PORT, RADIO_BAUD)
    usb   = init_serial("/dev/ttyGS0", 115200)

    print("Mock data transmitting...")

    while True:
        row      = mock_row()
        csv_line = ",".join(str(x) for x in row)

        write_log(row)
        send(radio, csv_line)
        send(usb, csv_line)

        print(csv_line, flush=True)
        time.sleep(1.0)

if __name__ == "__main__":
    main()