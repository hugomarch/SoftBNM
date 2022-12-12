from datetime import datetime, timedelta

def convert_datetime_in_timestamp(input_datetime, origin_datetime = datetime.strptime("1800-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")):
    """ return a timestamp equal to the number of hours elapsed between input and origin """
    return int((input_datetime - origin_datetime).total_seconds()//3600)

def convert_timestamp_in_datetime(input_timestamp, origin_datetime = datetime.strptime("1800-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")):
    """ return a datetime equal to the origin datetime + hours equal to input_timestamp """
    return origin_datetime + timedelta(hours = input_timestamp)