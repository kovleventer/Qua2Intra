import json

SONG_NAME = "music.ogg"
ICON_NAME = "icon.png" # TODO eliminate redundancy

I_STRINGS = ["", "[Left]", "[Up]", "[Up-Left]",
             "[Down]", "[Down-Left]", "[Up-Down]", "[Up-Down-Left]",
             "[Right]", "[Right-Left]", "[Up-Right]", "[Up-Right-Left]",
             "[Right-Down]", "[Right-Down-Left]", "[Up-Right-Down]", "[Up-Right-Down-Left]"]

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
    conf["speed"] = speed_magic(meta["arccount"], meta["length"])
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
