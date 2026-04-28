import board
import busio
import adafruit_bno055

_i2c = busio.I2C(board.SCL, board.SDA)
_sensor = adafruit_bno055.BNO055_I2C(_i2c)

def _safe_tuple(value, length=3):
    if value is None:
        return [0.0] * length
    return [0.0 if x is None else x for x in value]

def read_imu():
    gyro = _safe_tuple(_sensor.gyro)          # rad/s
    accel = _safe_tuple(_sensor.acceleration) # m/s^2
    mag = _safe_tuple(_sensor.magnetic)       # microtesla

    return {
        "ang_vel_x": gyro[0],
        "ang_vel_y": gyro[1],
        "ang_vel_z": gyro[2],
        "accel_x": accel[0],
        "accel_y": accel[1],
        "accel_z": accel[2],
        "mag_x": mag[0],
        "mag_y": mag[1],
        "mag_z": mag[2],
    }