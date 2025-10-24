import os
import math
MAIN_PATH = os.path.dirname(os.path.abspath(__file__))
MAP_NAME = "kraka"

def time_converter(time_str):
    split_time = time_str.split(":")
    length = len(split_time)
    time_seconds = 0
    for i in range(length):
        time_seconds += float(split_time[(length-1)-i]) * (60**i)
    return time_seconds

def time_to_string(time_secs):
    h = str(math.floor(time_secs / 3600))
    m = str(math.floor((time_secs - int(h)*3600) / 60))
    s = str(round(time_secs - int(h)*3600 - int(m)*60, 2)).split(".")
    if h != "0":
        return f"{h}:{m.zfill(2)}:{s[0].zfill(2)}.{s[1].ljust(2, '0')}"
    elif m != "0":
        return f"{m}:{s[0].zfill(2)}.{s[1].ljust(2, '0')}"
    else:
        return f"{s[0]}.{s[1].ljust(2, '0')}"
    
def key(input):
    return input.split(" ")[2]

def respawn_time(input):
    return input.split(" ")[0]

def input_times(input):
    return input.split(" ")[0].split("-")

sector_file = open(f"{MAIN_PATH}/processed/{MAP_NAME}_sector.txt", "r")



sector_file.close()
    

    
    
    





