import time
from datetime import datetime

from gps import read_gps
from imu import read_imu
from logger import init_log, write_log_row
from radio import send_radio
from usb_stream import send_usb

def build_row():
    gps_data = read_gps()
    imu_data = read_imu()

    timestamp = datetime.now().isoformat()

    row = [
        timestamp,
        gps_data["latitude"],
        gps_data["longitude"],
        gps_data["elevation"],
        gps_data["satellites"],
        imu_data["ang_vel_x"],
        imu_data["ang_vel_y"],
        imu_data["ang_vel_z"],
        imu_data["accel_x"],
        imu_data["accel_y"],
        imu_data["accel_z"],
        imu_data["mag_x"],
        imu_data["mag_y"],
        imu_data["mag_z"]
    ]
    return row

def main():
    init_log()

    while True:
        row = build_row()
        csv_line = ",".join(str(x) for x in row)

        write_log_row(row)
        send_usb(csv_line)
        send_radio(csv_line)

        time.sleep(1.0)

if __name__ == "__main__":
    main()