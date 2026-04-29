import serial
import time
from config import RADIO_PORT, RADIO_BAUD

_radio = None

def init_radio():
    global _radio
    try:
        _radio = serial.Serial(RADIO_PORT, RADIO_BAUD, timeout=1)
    except Exception as e:
        print(f"Radio not available: {e}", flush=True)
        _radio = None

def send_radio(data_line):
    if _radio is None:
        return
    try:
        _radio.write((data_line + "\n").encode("utf-8"))
        _radio.flush()
    except Exception as e:
        print(f"Radio send failed: {e}", flush=True)