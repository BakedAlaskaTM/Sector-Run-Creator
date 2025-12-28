import os
import functions
from pygbx import Gbx, GbxType
import generate_input_file

import math

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


def int16_to_headingangle(x: int) -> float:
    if not -32768 <= x <= 32767:
        raise ValueError("Input must be in range [-32768, 32767]")
    return (x / 32768) * math.pi

def int16_to_pitchangle(x: int) -> float:
    if not -32768 <= x <= 32767:
        raise ValueError("Input must be in range [-32768, 32767]")
    return (x / 32768) * (math.pi / 2)

def int8_to_headingangle(x: int) -> float:
    if not -128 <= x <= 127:
        raise ValueError("Input must be in range [-128, 127]")
    return (x / 128) * math.pi

def int8_to_pitchangle(x: int) -> float:
    if not -128 <= x <= 127:
        raise ValueError("Input must be in range [-128, 127]")
    return (x / 128) * (math.pi / 2)


MAIN_PATH = os.path.dirname(os.path.abspath(__file__))
MAP_NAME = ""

g = Gbx("Croco.Replay.Gbx")

try:
    replay = g.get_class_by_id(GbxType.REPLAY_RECORD)
    track = replay.track
except AttributeError:
    replay = g.get_class_by_id(GbxType.REPLAY_RECORD_OLD)
track = replay.track
challenge = track.get_class_by_id(GbxType.CHALLENGE)
ghost = g.get_class_by_id(GbxType.CTN_GHOST)

print(ghost.sample_period)
print(ghost.cp_times)
cp_positions = []

for cp_time in ghost.cp_times[0:-1]:
    current_record = ghost.records[round(cp_time / ghost.sample_period)]
    offset_time = cp_time % ghost.sample_period
    real_speed = int16_to_speed(current_record.speed)
    vpitch = int8_to_pitchangle(current_record.vel_pitch)
    vheading = int8_to_headingangle(current_record.vel_heading)
    speed_x = real_speed * math.cos(vpitch) * math.cos(vheading)
    speed_y = real_speed * math.cos(vpitch) * math.sin(vheading)
    speed_z = real_speed * math.sin(vpitch)
    offset_x = speed_x * (offset_time / 1000)
    offset_y = speed_y * (offset_time / 1000)
    offset_z = speed_z * (offset_time / 1000)
    cp_positions.append(current_record.get_block_position(xoff=offset_x, yoff=offset_y, zoff=offset_z).as_array())
    print(f"{len(cp_positions)}: {cp_positions[-1]}")
    print()


print()

rings = []
ring_cps = []

for block in challenge.blocks:
    if "CheckpointRing" in block.name:
        if block.name == "StadiumCheckpointRingV":
            rings.append(["V", block.position.as_array()])
        else:
            rings.append(["H", block.position.as_array()])

for i in range(len(cp_positions)):
    if check_ring_match(cp_positions[i], rings):
        ring_cps.append(i+1)
        print(f"CP {i+1} is a ring checkpoint.")



