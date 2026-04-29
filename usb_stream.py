import os
import select

_usb = None

def init_usb():
    global _usb
    try:
        _usb = open("/dev/ttyGS0", "wb", buffering=0)
    except Exception as e:
        print(f"USB not available: {e}", flush=True)
        _usb = None

def send_usb(data_line):
    global _usb
    if _usb is None:
        return
    try:
        _, ready, _ = select.select([], [_usb.fileno()], [], 0.5)
        if ready:
            os.write(_usb.fileno(), (data_line + "\n").encode("utf-8"))
            print(data_line, flush=True)
        else:
            print("USB not ready, skipping", flush=True)
    except OSError:
        print("USB disconnected, skipping", flush=True)
        try:
            _usb.close()
        except:
            pass
        _usb = None