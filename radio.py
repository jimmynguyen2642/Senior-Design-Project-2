import serial
import time
from config import RADIO_PORT, RADIO_BAUD

_radio = serial.Serial(RADIO_PORT, RADIO_BAUD, timeout=1)

def send_radio(data_line):
    _radio.write((data_line + "\n").encode("utf-8"))

if __name__ == "__main__":
    while True:
        send_radio("HELLO FROM PI")
        print("sent")
        time.sleep(1)