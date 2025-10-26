import os
import functions
from pygbx import Gbx, GbxType
import generate_input_file

MAIN_PATH = os.path.dirname(os.path.abspath(__file__))
MAP_NAME = "kack"

g = Gbx("kack.Replay.Gbx")

try:
    replay = g.get_class_by_id(GbxType.REPLAY_RECORD)
    track = replay.track
except AttributeError:
    replay = g.get_class_by_id(GbxType.REPLAY_RECORD_OLD)
track = replay.track
challenge = track.get_class_by_id(GbxType.CHALLENGE)

print(challenge.map_name.strip("/"))

