import serial

ser = serial.Serial("COM3", 115200)

while True:
    print(ser.readline())