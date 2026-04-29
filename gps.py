import board
import busio
import adafruit_gps

_i2c = busio.I2C(board.SCL, board.SDA)
_gps = adafruit_gps.GPS_GtopI2C(_i2c, debug=False)

_gps.send_command(b"PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")
_gps.send_command(b"PMTK220,1000")

def read_gps():
    _gps.update()
    return {
        "latitude":  _gps.latitude   if _gps.latitude   is not None else 0.0,
        "longitude": _gps.longitude  if _gps.longitude  is not None else 0.0,
        "elevation": _gps.altitude_m if _gps.altitude_m is not None else 0.0,
        "satellites": _gps.satellites if _gps.satellites is not None else 0,
    }