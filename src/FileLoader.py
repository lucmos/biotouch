# -*- coding: utf-8 -*-

import os
import json
import pandas
from src.Chronometer import Chrono

RES_FOLDER = "../res/Biotouch"
FILE_EXTENSION = ".json"

# ***************** json fields ***************** #


DATE = "date"

MOVEMENT_POINTS = "movementPoints"
TOUCH_DOWN_POINTS = "touchDownPoints"
TOUCH_UP_POINTS = "touchUpPoints"
SAMPLED_POINTS = "sampledPoints"
WORD_NUMBER = "wordNumber"

TIME = "time"
COMPONENT = "component"
X = "x"
Y = "y"

SESSION_DATA = "sessionData"
NAME = "name"
SURNAME = "surname"
AGE = "age"

GENDER = "gender"
HANDWRITING = "handwriting"
ID = "id"
TOTAL_WORD_NUMBER = "totalWordNumber"

DEVICE_DATA = "deviceData"
DEVICE_FINGERPRINT = "deviceFingerPrint"
DEVICE_MODEL = "deviceModel"
HEIGHT_PIXELS = "heigthPixels"
WIDTH_PIXELS = "widthPixels"
XDPI = "xdpi"
YDPI = "ydpi"

# Json structure

JSON_FIELDS = [
    DATE,
    MOVEMENT_POINTS,
    TOUCH_DOWN_POINTS,
    TOUCH_UP_POINTS,
    SAMPLED_POINTS,
    WORD_NUMBER,
    SESSION_DATA,
]

SESSION_DATA_FIELDS = [
    NAME,
    SURNAME,
    AGE,
    GENDER,
    HANDWRITING,
    ID,
    TOTAL_WORD_NUMBER,
    DEVICE_DATA,
]

DEVICE_DATA_FIELDS = [
    DEVICE_FINGERPRINT,
    DEVICE_MODEL,
    HEIGHT_PIXELS,
    WIDTH_PIXELS,
    XDPI,
    YDPI,
]

POINTS = [
    COMPONENT,
    X,
    Y,
]

TIMED_POINTS = POINTS + [TIME]


# *********************************************** #

# todo implementa singleton
class FileLoader:
    def __init__(self, base_folder=RES_FOLDER):
        self.base_folder = base_folder
        self.jsons_data = []
        self.id_mapping = {}
        self.data_frames = None

    @staticmethod
    def decode(json_file):
        return json.load(json_file)

    def load_data(self):
        if self.jsons_data:
            return self.jsons_data

        chrono = Chrono("Reading json files... ")
        # todo togli
        # for i in range(10):
        for root, dirs, files in os.walk(self.base_folder, True, None, False):
            for json_file in files:
                if json_file and json_file.endswith(FILE_EXTENSION):
                    json_path = os.path.realpath(os.path.join(root, json_file))
                    with open(json_path, 'r') as f:
                        self.jsons_data.append(self.decode(f))
        chrono.end()
        return self.jsons_data

    def get_dataframes(self):
        if self.data_frames and self.id_mapping:
            return self.id_mapping, self.data_frames
        self.load_data()

        chrono = Chrono("Creating dataframes...")

        mov_dataframes = {}
        up_dataframes = {}
        down_dataframes = {}
        sample_dataframes = {}

        for word_id, single_word_data in enumerate(self.jsons_data):
            self.id_mapping[word_id] = single_word_data

            movements_points_dict = self._from_timed_points(word_id, single_word_data[MOVEMENT_POINTS])
            touch_up_points_dict = self._from_timed_points(word_id, single_word_data[TOUCH_UP_POINTS])
            touch_down_point_dict = self._from_timed_points(word_id, single_word_data[TOUCH_DOWN_POINTS])
            sampled_points_dict = self._from_untimed_points(word_id, single_word_data[SAMPLED_POINTS])

            assert movements_points_dict
            assert touch_down_point_dict
            assert touch_up_points_dict
            assert sampled_points_dict

            mov_dataframes[word_id] = pandas.DataFrame(movements_points_dict)
            up_dataframes[word_id] = pandas.DataFrame(touch_up_points_dict)
            down_dataframes[word_id] = pandas.DataFrame(touch_down_point_dict)
            sample_dataframes[word_id] = pandas.DataFrame(sampled_points_dict)

        self.data_frames = {MOVEMENT_POINTS: mov_dataframes, TOUCH_UP_POINTS: up_dataframes,
                            TOUCH_DOWN_POINTS: down_dataframes, SAMPLED_POINTS: sample_dataframes}

        chrono.end()
        return self.id_mapping, self.data_frames

    @staticmethod
    def _from_timed_points(word_id, points_data):
        init_len = len(points_data)
        points_dict = {ID: [None] * init_len, TIME: [None] * init_len,
                       X: [None] * init_len, Y: [None] * init_len, COMPONENT: [None] * init_len}
        for i, point in enumerate(points_data):
            points_dict[ID][i] = word_id
            points_dict[TIME][i] = point[TIME]
            points_dict[X][i] = point[X]
            points_dict[Y][i] = point[Y]
            points_dict[COMPONENT][i] = point[COMPONENT]
        return points_dict

    @staticmethod
    def _from_untimed_points(word_id, points_data):
        init_len = sum((len(x) for x in points_data))
        points_dict = {ID: [None] * init_len, X: [None] * init_len, Y: [None] * init_len, COMPONENT: [None] * init_len}
        counter = 0
        for current_component, points in enumerate(points_data):
            for point in points:
                points_dict[ID][counter] = word_id
                points_dict[X][counter] = point[X]
                points_dict[Y][counter] = point[Y]
                points_dict[COMPONENT][counter] = current_component
                counter += 1

        return points_dict
