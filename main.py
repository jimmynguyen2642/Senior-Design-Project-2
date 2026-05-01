import time
from datetime import datetime
import threading
import RPi.GPIO as GPIO
from gps import read_gps
from imu import read_imu
from logger import init_log, write_log_row
from radio import send_radio, init_radio
from usb_stream import send_usb, init_usb

LED_PIN = 22
_gps_locked = False
_led_running = False

def init_led():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(LED_PIN, GPIO.OUT)
    GPIO.output(LED_PIN, GPIO.LOW)

def led_thread():
    global _gps_locked, _led_running
    state = False
    while _led_running:
        if _gps_locked:
            GPIO.output(LED_PIN, GPIO.HIGH)
            time.sleep(0.1)
        else:
            state = not state
            GPIO.output(LED_PIN, GPIO.HIGH if state else GPIO.LOW)
            time.sleep(0.25)  # flash 2x per second

def build_row():
    global _gps_locked
    gps_data = read_gps()
    imu_data = read_imu()
    _gps_locked = gps_data["satellites"] >= 3
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
    global _led_running
    init_usb()
    init_radio()
    init_led()

    _led_running = True
    t = threading.Thread(target=led_thread, daemon=True)
    t.start()

    try:
        while True:
            row, satellites = build_row()
            csv_line = ",".join(str(x) for x in row)
            send_usb(csv_line)
            send_radio(csv_line)
            time.sleep(1.0)
    except KeyboardInterrupt:
        _led_running = False
        GPIO.cleanup()

if __name__ == "__main__":
    main()