import os
import math
MAIN_PATH = os.path.dirname(os.path.abspath(__file__))
MAP_NAME = "PTC"

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
        return f"{h}:{m.zfill(2)}:{s[0].zfill(2)}.{s[1].ljust(2, "0")}"
    elif m != "0":
        return f"{m}:{s[0].zfill(2)}.{s[1].ljust(2, "0")}"
    else:
        return f"{s[0]}.{s[1].ljust(2, "0")}"
    
def key(input):
    return input.split(" ")[2]

def respawn_time(input):
    return input.split(" ")[0]

def input_times(input):
    return input.split(" ")[0].split("-")

splits = []

splits_file = open(f"{MAIN_PATH}/splits/{MAP_NAME}_splits.txt", "r")

inputs = []

inputs_file = open(f"{MAIN_PATH}/inputs/{MAP_NAME}_inputs.txt", "r")

for line in splits_file:
    splits.append(line.split(" ")[1].strip())

for line in inputs_file:
    inputs.append(line.strip())

splits_file.close()
inputs_file.close()

# Actual Algorithm
index = 0
respawns = []
for input in inputs:
    if key(input) == "enter":
        respawns.append(index)
    index += 1

input_blocks = []
slice_start = 0
slice_end = slice_start
for i in range(len(respawns)+1):
    if i == len(respawns):
        slice_end = len(inputs)-1
    else:
        slice_end = respawns[i]
    input_blocks.append(inputs[slice_start:slice_end+1])
    slice_start = slice_end

cp = 0
sectors = []
sector_indices = []
for i in range(len(input_blocks)-1):
    if time_converter(respawn_time(input_blocks[i][-1])) >= time_converter(splits[cp]) and time_converter(respawn_time(input_blocks[i][-1])) < time_converter(splits[cp+1]):
        sectors.append(input_blocks[i])
        sector_indices.append(i)
        cp += 1
    elif time_converter(respawn_time(input_blocks[i][-1])) >= time_converter(splits[cp+1]):
        for cp_num in range(cp, len(splits)):
            if time_converter(respawn_time(input_blocks[i][-1])) < time_converter(splits[cp_num]):
                cp = cp_num
                break
        sectors.append(input_blocks[i])
        sector_indices.append(i)
    if cp == len(splits)-1:
        break
sectors.append(input_blocks[-1])
sector_indices.append(len(input_blocks)-1)

sector_starts = ['0.00']
for sector in sectors:
    sector_starts.append(respawn_time(sector[0]))
sector_starts.remove(sector_starts[1])

for i in range(len(sector_indices)-1):
    for inputs in input_blocks[sector_indices[i]:sector_indices[i+1]]:
        for input in inputs:
            if "-" in input:
                if time_converter(input_times(input)[1]) >= time_converter(sector_starts[i+1]):
                    modified_input = f"{sector_starts[i+1]}-{input_times(input)[1]} press {key(input)}"
                    sectors[i+1].insert(0, modified_input)

for i in range(len(sectors)-1):
    last_input = sectors[i][-1]
    if time_converter(respawn_time(last_input)) > time_converter(sector_starts[i+1])-0.01:
        sectors[i].remove(sectors[i][-1])
    else:
        sectors[i][-1] = f"{respawn_time(last_input)} warp {time_to_string(time_converter(sector_starts[i+1])-0.01)}"

sector_file = open(f"{MAIN_PATH}/processed/{MAP_NAME}_sector.txt", "w")

for sector in sectors:
    for input in sector:
        sector_file.write(f"{input}\n")
    sector_file.write("\n")

sector_file.close()
    

    
    
    





