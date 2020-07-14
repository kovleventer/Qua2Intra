import json
import yaml
import os
from mutagen.mp3 import MP3
from shutil import copyfile

DIR_LEFT = 0x01
DIR_UP = 0x02
DIR_DOWN = 0x04
DIR_RIGHT = 0x08

Q_LANES = [0, DIR_LEFT, DIR_UP, DIR_DOWN, DIR_RIGHT]
I_STRINGS = ["", "[Left]", "[Up]", "[Up-Left]",
             "[Down]", "[Down-Left]", "[Up-Down]", "[Up-Down-Left]",
             "[Right]", "[Right-Left]", "[Up-Right]", "[Up-Right-Left]",
             "[Right-Down]", "[Right-Down-Left]", "[Up-Right-Down]", "[Up-Right-Down-Left]"]

STEAMPATH = "/home/kovlev/.local/share/Steam/"  # TODO
INTRAPATH = os.path.join(STEAMPATH, "steamapps/common/Intralism/Editor/")
QUAVERPATH = os.path.join(STEAMPATH, "steamapps/common/Quaver/Songs/")

SONG_NAME = "music.ogg"
ICON_NAME = "icon.png"

def speed_magic(arc_cnt, length):
    # TODO better handling
    return min(arc_cnt // length + 20, 36)

def write_intra_conf(path, arcs, meta):
    conf = {}
    conf["configVersion"] = 2
    conf["name"] = meta['title']
    conf["info"] = "Map automatically converted from Quaver"  # TODO difficulty, length and stuff
    conf["levelResources"] = []  # TODO at least simple bg
    conf["tags"] = ['Other']  # TODO extract from yaml
    conf["handCount"] = 1
    conf["moreInfoURL"] = ""
    conf["speed"] = speed_magic(meta["arccount"], meta["length"])  # TODO yea, something more adaptive
    conf["lives"] = 50
    conf["maxLives"] = conf["lives"]
    conf["musicFile"] = SONG_NAME
    conf["musicTime"] = meta["length"]
    conf["iconFile"] = ICON_NAME
    conf["environmentType"] = -1
    conf["unlockConditions"] = []
    conf["hidden"] = False
    conf["checkpoints"] = []
    conf["events"] = []
    for time, lane in sorted(arcs.items()):
        conf["events"].append(dict(time=time / 1000, data=['SpawnObj', I_STRINGS[lane]]))
    conf["e"] = ""
    json_data = json.dumps(conf)
    with open(path, "wt") as f:
        f.write(json_data)


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
            os.system("ffmpeg -i \"" + os.path.join(folder, meta["song"]) + "\" -c:a libvorbis -q:a 4 " + os.path.join(destpath, SONG_NAME)) # TODO multiplatform
            copyfile(os.path.join(folder, meta["image"]), os.path.join(destpath, ICON_NAME))

# example call
convert_folder("972 - 403")
