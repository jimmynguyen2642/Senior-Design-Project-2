CSV_HEADER = [
    "timestamp",
    "latitude",
    "longitude",
    "elevation",
    "satellites",
    "ang_vel_x",
    "ang_vel_y",
    "ang_vel_z",
    "accel_x",
    "accel_y",
    "accel_z",
    "mag_x",
    "mag_y",
    "mag_z"
]

LOG_FILE = "sensor_log.csv"
RADIO_PORT = "/dev/serial0"   # example, may change later
RADIO_BAUD = 9600
SAMPLE_PERIOD = 1.0