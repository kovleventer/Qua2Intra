from zipfile import ZipFile
import os
import configparser

#aint workin yet
def load_osu(filaname, item):
    with ZipFile(filename, 'r') as zip: # multiple file handlers on the same file, but since but both of them are in read mode so should be fine
        txt = zip.read(item).decode("utf-8")
    config = configparser.ConfigParser()
    txt = txt[txt.index("\n"):] # Ignore first line
    config.read_string(txt)
    print(config['General'])
    return None, None

def convert_file(filename):
    with ZipFile(filename, 'r') as zip:
        nl = zip.namelist()
        for item in nl:
            if item.endswith(".osu"):
                arcs, meta = load_osu(filename, item)


if __name__ == "__main__":
    filename = '7380 Caramell - Caramelldansen (Speedycake Remix).osz'
    convert_file(filename)
