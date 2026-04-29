import serial
import os
import select

_usb = None

def init_usb():
    global _usb
    try:
        _usb = serial.Serial("/dev/ttyGS0", 115200, timeout=1)
        _usb.nonblocking()
    except Exception as e:
        print(f"USB not available: {e}", flush=True)
        _usb = None

def send_usb(data_line):
    if _usb is None:
        return
    try:
        # check if writable within 0.5s, skip if not
        _, ready, _ = select.select([], [_usb.fileno()], [], 0.5)
        if ready:
            os.write(_usb.fileno(), (data_line + "\n").encode("utf-8"))
            print(data_line, flush=True)
        else:
            print("USB not ready, skipping", flush=True)
    except Exception as e:
        print(f"USB send failed: {e}", flush=True)