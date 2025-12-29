import math
from pygbx import Gbx, GbxType
import generate_input_file
import os
import re
import unidecode

def check_ring_match(cp_position, rings):
    for ring in rings:
        if ring[0] == "V":
            if cp_position[0] == ring[1][0] and cp_position[1]-ring[1][1] <= 4 and cp_position[2] == ring[1][2]:
                return True
        else:
            if cp_position == ring[1]:
                return True
    return False

def int16_to_speed(x: int) -> float:
    if not -32768 <= x <= 32767:
        raise ValueError("Input must be int16: [-32768, 32767]")
    
    if x == -32768:
        return 0.0
    return math.exp(x / 1000.0)

def int8_to_headingangle(x: int) -> float:
    if not -128 <= x <= 127:
        raise ValueError("Input must be in range [-128, 127]")
    return (x / 128) * math.pi

def int8_to_pitchangle(x: int) -> float:
    if not -128 <= x <= 127:
        raise ValueError("Input must be in range [-128, 127]")
    return (x / 128) * (math.pi / 2)

def calculate_offset(current_record, offset_time):
    real_speed = int16_to_speed(current_record.speed)
    vpitch = int8_to_pitchangle(current_record.vel_pitch)
    vheading = int8_to_headingangle(current_record.vel_heading)
    speed_x = real_speed * math.cos(vpitch) * math.cos(vheading)
    speed_y = real_speed * math.cos(vpitch) * math.sin(vheading)
    speed_z = real_speed * math.sin(vpitch)
    offset_x = speed_x * (offset_time / 1000)
    offset_y = speed_y * (offset_time / 1000)
    offset_z = speed_z * (offset_time / 1000)
    return [offset_x, offset_y, offset_z]

def find_ring_checkpoints(challenge: GbxType.CHALLENGE, ghost: GbxType.CTN_GHOST):
    cp_positions = []
    rings = []
    ring_cps = []
    for cp_time in ghost.cp_times[0:-1]:
        current_record = ghost.records[round(cp_time / ghost.sample_period)]
        offset_time = cp_time % ghost.sample_period
        offsets = calculate_offset(current_record, offset_time)
        cp_positions.append(current_record.get_block_position(xoff=offsets[0], yoff=offsets[1], zoff=offsets[2]).as_array())
    for block in challenge.blocks:
        if "CheckpointRing" in block.name:
            if block.name == "StadiumCheckpointRingV":
                rings.append(["V", block.position.as_array()])
            else:
                rings.append(["H", block.position.as_array()])
    for i in range(len(cp_positions)):
        if check_ring_match(cp_positions[i], rings):
            ring_cps.append(i+1)
    return ring_cps

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

def get_cp_times(ghost: GbxType.CTN_GHOST):
    ghost_times = []
    for time in ghost.cp_times:
        ghost_times.append(time_to_string(time/1000))
    return [ghost_times, len(ghost_times)-1]

def get_map_info(challenge: GbxType.CHALLENGE, ghost: GbxType.CTN_GHOST):
    regex_string = '[$][a-fA-F0-9][a-fA-F0-9][a-fA-F0-9]|[$][a-zA-Z]'
    regex = re.sub(regex_string,'', challenge.map_name)
    author = challenge.map_author
    ring_cps = find_ring_checkpoints(challenge, ghost)
    return [regex.strip(), author, ring_cps]
    
def create_file(dir, map_name, inputs):
    regex_string = '[॥\\/:*?"<>|]'
    regex = re.sub(regex_string, '', map_name)
    regex = unidecode.unidecode(regex)
    regex = '_'.join(regex.split())
    processed_file = open(f"{dir}/{regex}_sector.txt", "w")
    for block in inputs:
        for input in block:
            processed_file.write(f"{input}\n")
        processed_file.write("\n")

    processed_file.close()
    return f"{regex}_sector.txt"

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
        
    return [inputs, time_offset]

def generate_sector_inputs(file_path, option=2, remove_rings=None):
    if remove_rings is None:
        remove_rings = []
    if file_path == '':
        return
    
    g = Gbx(file_path)
    try:
        replay = g.get_class_by_id(GbxType.REPLAY_RECORD)
        track = replay.track
    except AttributeError:
        replay = g.get_class_by_id(GbxType.REPLAY_RECORD_OLD)
    track = replay.track
    challenge = track.get_class_by_id(GbxType.CHALLENGE)
    ghost = g.get_class_by_id(GbxType.CTN_GHOST)
    [ghost_times, num_cps] = get_cp_times(ghost)
    [map_name, author, ring_cps] = get_map_info(challenge, ghost)
    ghost_times_filtered = []
    for i in range(len(ghost_times)):
        if (i) not in remove_rings:
            ghost_times_filtered.append(ghost_times[i])

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

    if option == 0:
        return [map_name, author, num_cps, ring_cps, ghost_times[-1], [raw_inputs]]
    inputs = immediate_respawns(ghost_times_filtered, create_segmented_run(ghost_times_filtered, inputs))
    if option == 1:
        return [map_name, author, num_cps, ring_cps, time_to_string(time_converter(ghost_times[-1])), inputs]

    [processed_inputs, time_save] = no_warp(inputs)

    return [map_name, author, num_cps, ring_cps, time_to_string(time_converter(ghost_times[-1]) - time_save), processed_inputs]

def grid_positions(labels, prefer_tall=True):
    n = len(labels)

    if n == 0:
        return [], 0, 0

    cols = math.ceil(math.sqrt(n))
    rows = math.ceil(n / cols)

    # Optional: swap to prefer tall layouts
    if prefer_tall and rows < cols:
        rows, cols = cols, rows

    positions = []
    for i, label in enumerate(labels):
        row = i % rows
        col = i // rows
        positions.append((label, row, col))

    return positions, rows, cols