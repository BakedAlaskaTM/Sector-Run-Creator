import math
from pygbx import Gbx, GbxType
import generate_input_file
import os

def read_config(filename: str="config.txt", settings: list=["DESTINATION"]):
    config_file = open(filename, "r")
    config_file = open("config.txt", "r")
    config_lines = config_file.read().split("\n")
    config_file.close()

    setting_dict = {}
    for line in config_lines:
        if line != "":
            line_split = line.split(":")
            current_setting = line_split[0].strip()
            value = ":".join(line_split[1:len(line_split)]).strip()
            for setting in settings:
                if current_setting == setting:
                    setting_dict[setting] = value
                    break
    return setting_dict


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

def get_cp_times(file_path):
    g = Gbx(file_path)

    ghost = g.get_class_by_id(GbxType.CTN_GHOST)

    ghost_times = ghost.cp_times
    for i in range(len(ghost_times)):
        ghost_times[i] = time_to_string(ghost_times[i]/1000)
    return ghost_times

def get_map_name(file_path):
    g = Gbx(file_path)
    try:
        replay = g.get_class_by_id(GbxType.REPLAY_RECORD)
        track = replay.track
    except AttributeError:
        replay = g.get_class_by_id(GbxType.REPLAY_RECORD_OLD)
    track = replay.track
    challenge = track.get_class_by_id(GbxType.CHALLENGE)
    return challenge.map_name.strip("/")
    

def create_file(dir, map_name, inputs):
    processed_file = open(f"{dir}/{map_name}_sector.txt", "w")
    for block in inputs:
        for input in block:
            processed_file.write(f"{input}\n")
        processed_file.write("\n")

    processed_file.close()

def read_splits(main_path, map_name):
    splits = []
    splits_file = open(f"{main_path}/splits/{map_name}_splits.txt", "r")
    for line in splits_file:
        splits.append(line.split(" ")[1].strip())
    splits_file.close()
    return splits

def read_inputs(main_path, map_name, processed=False):
    inputs = []
    if processed:
        inputs_file = open(f"{main_path}/processed/{map_name}_sector.txt", "r")
        temp = inputs_file.read().split("\n\n")
        for block in temp:
            inputs.append(block.split("\n"))
        inputs.pop(-1)
    else:
        inputs_file = open(f"{main_path}/inputs/{map_name}_inputs.txt", "r")
        for line in inputs_file:
            inputs.append(line.strip())
    inputs_file.close()
    return inputs

def create_segmented_run(splits, inputs):
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
    
    return sectors

def immediate_respawns(splits, inputs):
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
    
    return inputs

def no_warp(inputs):
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
        
    return inputs

def generate_sector_file(file_path, save_dir):
    ghost_times = get_cp_times(file_path)
    map_name = get_map_name(file_path)
    with open(f"result.txt", 'w+') as f:
        generate_input_file.process_path(file_path, f.write)
    
    raw_inputs_file = open("result.txt", "r")
    raw_inputs = raw_inputs_file.read().split("\n")
    raw_inputs_file.close()
    os.remove("result.txt")
    raw_inputs.pop(-1)

    inputs = []
    for line in raw_inputs:

        if "enter" in line:
            inputs.append(f"{time_to_string(int(input_times(line)[0])/1000)} press enter")
        else:
            inputs.append(f"{time_to_string(int(input_times(line)[0])/1000)}-{time_to_string(int(input_times(line)[1])/1000)} press {key(line)}")

    processed_inputs = no_warp(immediate_respawns(ghost_times, create_segmented_run(ghost_times, inputs)))

    create_file(save_dir, map_name, processed_inputs)

    return processed_inputs