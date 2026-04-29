import board
import busio
import digitalio
import adafruit_sdcard
import storage

# SPI setup
spi = busio.SPI(board.SCK, board.MOSI, board.MISO)

# CS pin (GPIO8 / Pin 24)
cs = digitalio.DigitalInOut(board.D8)

# Initialize SD card
sdcard = adafruit_sdcard.SDCard(spi, cs)

# Mount filesystem
vfs = storage.VfsFat(sdcard)
storage.mount(vfs, "/sd")

print("SD card mounted!")

# Write file
with open("/sd/test.txt", "w") as f:
    f.write("Hello from Raspberry Pi!\n")

print("Write successful!")

# Read file back
with open("/sd/test.txt", "r") as f:
    print("File contents:")
    print(f.read())