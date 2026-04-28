import serial
from config import RADIO_PORT, RADIO_BAUD

_radio = serial.Serial(RADIO_PORT, RADIO_BAUD, timeout=1)

def send_radio(data_line):
    _radio.write((data_line + "\n").encode("utf-8"))