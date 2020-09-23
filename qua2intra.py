import json
import yaml
import os
from mutagen.mp3 import MP3
from shutil import copyfile
from config import *

from intra import write_intra_conf

DIR_LEFT = 0x01
DIR_UP = 0x02
DIR_DOWN = 0x04
DIR_RIGHT = 0x08

Q_LANES = [0, DIR_LEFT, DIR_UP, DIR_DOWN, DIR_RIGHT]


SONG_NAME = "music.ogg"
ICON_NAME = "icon.png"


def load_qua(path):
    with open(path) as f:
        y = yaml.load(f)

    arcs = {}
    for hitObject in y['HitObjects']:
        if 'StartTime' in hitObject:
            t = hitObject['StartTime']
        else:
            t = 0
        lane = Q_LANES[hitObject['Lane']]
        if t in arcs:
            arcs[t] = arcs[t] | lane
        else:
            arcs[t] = lane

    meta = {}
    meta["title"] = y['Artist'] + " - " + y['Title'] + " (" + y['DifficultyName'] + ")"
    meta["song"] = y["AudioFile"]
    meta["image"] = y["BackgroundFile"]
    meta["arccount"] = len(y['HitObjects'])
    meta["valid"] = (y["Mode"] == "Keys4")

    return arcs, meta

def convert_folder(foldername):
    folder = os.path.join(QUAVERPATH, foldername)
    for file in os.listdir(folder):
        if file.endswith(".qua"):
            arcs, meta = load_qua(os.path.join(folder, file))
            h = abs(hash(frozenset(arcs.items())))
            destpath = os.path.join(INTRAPATH, str(h))

            if not meta["valid"]:
                print("Skipping invalid song: " + meta["title"])
                continue

            try:
                os.mkdir(destpath)
            except OSError:
                pass
            meta["length"] = MP3(os.path.join(folder, meta["song"])).info.length
            write_intra_conf(os.path.join(destpath, "config.txt"), arcs, meta)
            os.system("ffmpeg -i \"" + os.path.join(folder, meta["song"]) + "\" -c:a libvorbis -q:a 4 -map a " + os.path.join(destpath, SONG_NAME)) # TODO multiplatform
            copyfile(os.path.join(folder, meta["image"]), os.path.join(destpath, ICON_NAME))

# example call
if __name__ == "__main__":
    convert_folder("2758 - 382")
