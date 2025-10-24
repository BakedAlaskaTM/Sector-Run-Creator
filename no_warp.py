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

def warp_destination(input):
    return input.split(" ")[2]

inputs = []

inputs_file = open(f"{MAIN_PATH}/processed/{MAP_NAME}_respawns.txt", "r")

temp = inputs_file.read().split("\n\n")
for block in temp:
    inputs.append(block.split("\n"))
inputs.pop(-1)

inputs_file.close()

# Actual algorithm

time_offset = 0

for block_index in range(len(inputs)-1):
    warp_input = inputs[block_index].pop(-1)
    time_offset += time_converter(warp_destination(warp_input)) - time_converter(input_times(warp_input)[0]) - 0.01
    time_offset = round(time_offset, 2)
    for input_index in range(len(inputs[block_index+1])-1):
        input = inputs[block_index+1][input_index]
        if "-" in input:
            inputs[block_index+1][input_index] = f"{time_to_string(time_converter(input_times(input)[0])-time_offset)}-{time_to_string(time_converter(input_times(input)[1])-time_offset)} press {key(input)}"
        else:
            inputs[block_index+1][input_index] = f"{time_to_string(time_converter(respawn_time(input))-time_offset)} press {key(input)}"

input = inputs[-1][-1]
if "-" in input:
    inputs[-1][-1] = f"{time_to_string(time_converter(input_times(input)[0])-time_offset)}-{time_to_string(time_converter(input_times(input)[1])-time_offset)} press {key(input)}"
else:
    inputs[-1][-1] = f"{time_to_string(time_converter(respawn_time(input))-time_offset)} press {key(input)}"

updated_file = open(f"{MAIN_PATH}/processed/{MAP_NAME}_no_warp.txt", "w")

for blocks in inputs:
    for input in blocks:
        updated_file.write(f"{input}\n")
    updated_file.write("\n")

updated_file.close()