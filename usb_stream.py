import serial

ser = serial.Serial("/dev/ttyUSB0", 9600)

def send_usb(data_line):
    ser.write((data_line + "\n").encode())