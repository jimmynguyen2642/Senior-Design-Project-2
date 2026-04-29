import serial

_usb = None

def init_usb():
    global _usb
    try:
        _usb = serial.Serial("/dev/ttyGS0", 115200, timeout=1)
    except Exception as e:
        print(f"USB not available: {e}", flush=True)
        _usb = None

def send_usb(data_line):
    if _usb is None:
        return
    try:
        _usb.write((data_line + "\n").encode("utf-8"))
        _usb.flush()
        print(data_line, flush=True)
    except Exception as e:
        print(f"USB send failed: {e}", flush=True)