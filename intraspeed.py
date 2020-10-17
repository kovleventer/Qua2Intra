from intra import write_intra_conf
from config import INTRA_WORKSHOP_PATH, INTRAPATH
import os
import json
from intra import I_STRINGS
from shutil import copyfile
ICON_NAME = "icon.png"
SONG_NAME = "music.ogg"

# bunch of duplicate stuff TODO this better

def change_speed(foldername, new_speed):
    folder = os.path.join(INTRA_WORKSHOP_PATH, foldername)
    config = os.path.join(folder, "config.txt")
    with open(config) as file:
        conf = json.load(file)
    meta = {}
    arcs = {}
    meta["title"] = conf["name"] + "(" + str(new_speed) + ")"
    meta["song"] = conf["musicFile"]
    meta["image"] = conf["iconFile"]

    meta["arccount"] = 0
    for event in conf["events"]:
        t = event["time"] / new_speed
        action = event["data"][0]
        #print(event)
        if action != "SpawnObj":
            continue
        actionstr = event["data"][1]
        if actionstr[-2:] == ',0':
            actionstr = actionstr[:-2]
        idx = I_STRINGS.index(actionstr)
        arcs[int(t * 1000)] = idx
        meta["arccount"] += bin(idx).count('1')

    #print(arcs)

    meta["length"] = conf["musicTime"] / new_speed


    destpath = os.path.join(INTRAPATH, foldername + "_" + str(new_speed))
    try:
        os.mkdir(destpath)
    except OSError:
        pass
    write_intra_conf(os.path.join(destpath, "config.txt"), arcs, meta)
    copyfile(os.path.join(folder, meta["image"]), os.path.join(destpath, ICON_NAME))
    os.system("sox " + os.path.join(folder, meta["song"]) + " " + os.path.join(destpath, SONG_NAME) + " speed " + str(new_speed))

if __name__ == "__main__":
    change_speed("1877814777", 1.3)
