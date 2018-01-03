# -*- coding: utf-8 -*-

import os
import json


RES_FOLDER = "../res/Biotouch"
FILE_EXT = ".json"


class FileLoader:
    def __init__(self, base_folder):
        self.base_folder = base_folder
        self.data = []

    @staticmethod
    def decode(json_file):
        return json.load(json_file)

    def load_data(self):
        print(self.base_folder)
        for root, dirs, files in os.walk(self.base_folder, True, None, False):
            for json_file in files:
                if json_file and json_file.endswith(FILE_EXT):
                        json_path = os.path.realpath(os.path.join(root, json_file))
                        with open(json_path, 'r') as f:
                            self.data.append(self.decode(f))
        return self.data
