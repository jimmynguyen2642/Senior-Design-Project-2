import time
import csv
import os
import select
import random
import math
import serial
import RPi.GPIO as GPIO
from datetime import datetime

#  Config 
LOG_FILE   = "/home/admin/Senior-Design-Project-2/sensor_log.csv"
RADIO_PORT = "/dev/serial0"
RADIO_BAUD = 9600
USB_PORT   = "/dev/ttyGS0"
USB_BAUD   = 115200
LED_PIN    = 17

CSV_HEADER = [
    "timestamp", "latitude", "longitude", "elevation", "satellites",
    "ang_vel_x", "ang_vel_y", "ang_vel_z",
    "accel_x",   "accel_y",   "accel_z",
    "mag_x",     "mag_y",     "mag_z"
]

# Mock data state 
_t = 0.0  # time counter for smooth animation

def mock_row():
    global _t
    _t += 1.0

    # Simulate GPS locking on after 10 seconds
    satellites = 0 if _t < 10 else random.randint(4, 9)
    locked     = satellites >= 3

    return {
        "timestamp": datetime.now().isoformat(),
        "latitude":  36.138405 + math.sin(_t * 0.05) * 0.0005,
        "longitude": -97.066748 + math.cos(_t * 0.05) * 0.0005,
        "elevation": 285.10 + math.sin(_t * 0.1) * 2.0,
        "satellites": satellites,
        "ang_vel_x": math.sin(_t * 0.2) * 0.05,
        "ang_vel_y": math.cos(_t * 0.15) * 0.05,
        "ang_vel_z": math.sin(_t * 0.1) * 0.02,
        "accel_x":   math.sin(_t * 0.3) * 0.5,
        "accel_y":   math.cos(_t * 0.25) * 0.5,
        "accel_z":   9.81 + math.sin(_t * 0.1) * 0.1,
        "mag_x":     17.25 + math.sin(_t * 0.05) * 1.0,
        "mag_y":     -2.88 + math.cos(_t * 0.05) * 1.0,
        "mag_z":     -128.88 + math.sin(_t * 0.02) * 2.0,
        "locked":    locked,
    }

def row_to_list(d):
    return [
        d["timestamp"], d["latitude"], d["longitude"], d["elevation"],
        d["satellites"], d["ang_vel_x"], d["ang_vel_y"], d["ang_vel_z"],
        d["accel_x"], d["accel_y"], d["accel_z"],
        d["mag_x"], d["mag_y"], d["mag_z"]
    ]

# SD card / CSV logging 
def init_log():
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", newline="") as f:
            csv.writer(f).writerow(CSV_HEADER)
    print(f"Logging to {LOG_FILE}", flush=True)

def write_log(row):
    try:
        with open(LOG_FILE, "a", newline="") as f:
            csv.writer(f).writerow(row)
    except Exception as e:
        print(f"SD write error: {e}", flush=True)

# Serial helpers 
def init_serial(port, baud, name):
    try:
        s = serial.Serial(port, baud, timeout=1)
        print(f"{name} opened on {port}", flush=True)
        return s
    except Exception as e:
        print(f"{name} not available ({e})", flush=True)
        return None

def send(ser, line, name):
    if ser is None:
        return
    try:
        _, ready, _ = select.select([], [ser.fileno()], [], 0.5)
        if ready:
            ser.write((line + "\n").encode("utf-8"))
            ser.flush()
        else:
            print(f"{name} not ready, skipping", flush=True)
    except OSError:
        print(f"{name} disconnected", flush=True)

#  LED 
def init_led():
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(LED_PIN, GPIO.OUT)
        GPIO.output(LED_PIN, GPIO.LOW)
        print(f"LED on GPIO{LED_PIN}", flush=True)
    except Exception as e:
        print(f"LED init error: {e}", flush=True)

def update_led(locked, flash_state):
    try:
        if locked:
            GPIO.output(LED_PIN, GPIO.HIGH)
            return True
        else:
            new_state = not flash_state
            GPIO.output(LED_PIN, GPIO.HIGH if new_state else GPIO.LOW)
            return new_state
    except Exception:
        return flash_state

#  Main 
def main():
    print("=== LOCALIZATION DEVICE — DEMO MODE ===", flush=True)

    init_log()
    init_led()

    radio = init_serial(RADIO_PORT, RADIO_BAUD, "Radio/BT")
    usb   = init_serial(USB_PORT,   USB_BAUD,   "USB")

    flash_state = False
    loop = 0

    try:
        while True:
            loop += 1
            data     = mock_row()
            row      = row_to_list(data)
            csv_line = ",".join(str(round(x, 6) if isinstance(x, float) else x)
                                for x in row)

            # SD card
            write_log(row)

            # USB stream
            send(usb, csv_line, "USB")

            # Bluetooth/Radio
            send(radio, csv_line, "Radio")

            # LED
            flash_state = update_led(data["locked"], flash_state)

            # Console status
            status = "LOCKED" if data["locked"] else "SEARCHING"
            print(
                f"[{loop:04d}] GPS:{status}({int(data['satellites'])}sats) "
                f"lat={data['latitude']:.6f} "
                f"az={data['accel_z']:.2f}m/s²",
                flush=True
            )

            time.sleep(1.0)

    except KeyboardInterrupt:
        print("\nStopped.", flush=True)
        GPIO.cleanup()

if __name__ == "__main__":
    main()