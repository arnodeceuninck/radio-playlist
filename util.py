from datetime import datetime

def str_to_time(string):
    return datetime.strptime(string, "%Y-%m-%dT%H:%M:%S.%fZ") if string is not None else None