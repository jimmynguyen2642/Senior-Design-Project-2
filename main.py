import time
from datetime import datetime
import RPi.GPIO as GPIO

from gps import read_gps
from imu import read_imu
from logger import init_log, write_log_row
from radio import send_radio, init_radio
from usb_stream import send_usb, init_usb

LED_PIN = 23 #pin 16

def init_led():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(LED_PIN, GPIO.OUT)
    GPIO.output(LED_PIN, GPIO.LOW)

def update_led(satellites, flash_state):
    if satellites >= 3:
        GPIO.output(LED_PIN, GPIO.HIGH)  # solid on = locked
        return flash_state
    else:
        # flash while searching
        new_state = not flash_state
        GPIO.output(LED_PIN, GPIO.HIGH if new_state else GPIO.LOW)
        return new_state

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
    return row, gps_data["satellites"]

def main():
    # init_log()
    init_usb()
    init_radio()
    init_led()

    flash_state = False

    try:
        while True:
            row, satellites = build_row()
            csv_line = ",".join(str(x) for x in row)

            # write_log_row(row)
            send_usb(csv_line)
            send_radio(csv_line)
            flash_state = update_led(satellites, flash_state)

            time.sleep(1.0)
    except KeyboardInterrupt:
        GPIO.cleanup()

if __name__ == "__main__":
    main()