import serial

_usb = serial.Serial("/dev/ttyGS0", 115200, timeout=1)

def send_usb(data_line):
    _usb.write((data_line + "\n").encode("utf-8"))
    print(data_line, flush=True)