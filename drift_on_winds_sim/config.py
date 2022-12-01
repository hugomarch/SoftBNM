from datetime import datetime
import os

DB_FILE = "wind.db"
DAY_WIND_DATA_FILE = os.path.join("resources","one_day_data.pickle")

TIMESTAMP_MIN = 1569072
DATE_MIN = datetime.strptime("01-01-1979 00:00:00","%d-%m-%Y %H:%M:%S")

PRESSURE_LEVELS = [1000, 925, 850, 700, 600, 500, 400, 300, 250, 200, 150, 100, 70, 50, 30, 20, 10]
LAT_INTERVAL = 2.5
LON_INTERVAL = 2.5