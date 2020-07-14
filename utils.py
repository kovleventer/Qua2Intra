import os
import yaml

def get_folder_image_quaver(folder):
    for file in os.listdir(folder):
        if file.endswith(".qua"):
            with open(os.path.join(folder, file)) as f:
                y = yaml.load(f)
                return os.path.join(folder, y["BackgroundFile"])

def get_song_name_quaver(folder):
    for file in os.listdir(folder):
        if file.endswith(".qua"):
            with open(os.path.join(folder, file)) as f:
                y = yaml.load(f)
                return os.path.join(y['Artist'] + " - " + y["Title"])
