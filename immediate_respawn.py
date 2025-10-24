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

splits = []

splits_file = open(f"{MAIN_PATH}/splits/{MAP_NAME}_splits.txt", "r")

inputs = []

inputs_file = open(f"{MAIN_PATH}/processed/{MAP_NAME}_sector.txt", "r")

for line in splits_file:
    splits.append(line.split(" ")[1].strip())

temp = inputs_file.read().split("\n\n")
for block in temp:
    inputs.append(block.split("\n"))
inputs.pop(-1)

splits_file.close()
inputs_file.close()

# Actual Algorithm
current_cp = 1
for block_index in range(len(inputs)-1):
    final_input = inputs[block_index][-1]
    next_start_input = inputs[block_index + 1][0]
    while time_converter(splits[current_cp - 1]) <= time_converter(input_times(final_input)[0]):
        current_cp += 1
    if time_converter(splits[current_cp - 1]) > time_converter(input_times(next_start_input)[0]):
        current_cp -= 1

    while time_converter(input_times(inputs[block_index][-1])[0]) > time_converter(splits[current_cp - 1]):
        final_input = inputs[block_index].pop(-1)
        if "-" in final_input and time_converter(input_times(final_input)[1]) > time_converter(input_times(next_start_input)[0]):
            inputs[block_index + 1].insert(0, f"{input_times(next_start_input)[0]}-{input_times(final_input)[1]} press {key(final_input)}")
    for input_index in range(len(inputs[block_index])):
        input = inputs[block_index][input_index]
        if "-" in input and time_converter(input_times(input)[1]) > time_converter(splits[current_cp - 1]):
            inputs[block_index][input_index] = f"{input_times(input)[0]}-{time_to_string(time_converter(splits[current_cp - 1]))} press {key(input)}"

    inputs[block_index].append(f"{time_to_string(time_converter(splits[current_cp - 1]) + 0.01)} warp {time_to_string(time_converter(input_times(next_start_input)[0])-0.01)}")

updated_file = open(f"{MAIN_PATH}/processed/{MAP_NAME}_respawns.txt", "w")

for blocks in inputs:
    for input in blocks:
        updated_file.write(f"{input}\n")
    updated_file.write("\n")

updated_file.close()