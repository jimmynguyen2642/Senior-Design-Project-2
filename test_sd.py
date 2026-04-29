import spidev

# Test 1: SPI is responding
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 1000000
spi.mode = 0
resp = spi.xfer2([0xFF] * 10)
print("SPI response:", [hex(x) for x in resp])
spi.close()

# Test 2: SD card seen as block device
import os
if os.path.exists("/dev/sda"):
    print("SD card found at /dev/sda")
elif os.path.exists("/dev/sda1"):
    print("SD card found at /dev/sda1")
else:
    print("No SD block device found - wiring or overlay issue")