# -*- coding: utf-8 -*-
import os
import json
import pandas
from src.Chronometer import Chrono
import src.Utils as Utils

BIOTOUCH_FOLDER = "../res/Biotouch"
FILE_EXTENSION = ".json"
WORD_ID = "word_id"
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

# Utils
WORD_ID_POINTS = POINTS + [WORD_ID]
WORD_ID_TIMED_POINTS = TIMED_POINTS + [WORD_ID]


# *********************************************** #


class JsonLoader:
    def __init__(self, base_folder=BIOTOUCH_FOLDER):
        assert os.path.isdir(base_folder)

        self.base_folder = base_folder
        self._jsons_data = JsonLoader._load_jsons(base_folder)

        self.idword_dataword_mapping = {}
        self.iduser_datauser_mapping = {}
        self.idword_iduser_mapping = {}

        self.data_dicts = {MOVEMENT_POINTS: {x: [] for x in WORD_ID_TIMED_POINTS},
                           TOUCH_UP_POINTS: {x: [] for x in WORD_ID_TIMED_POINTS},
                           TOUCH_DOWN_POINTS: {x: [] for x in WORD_ID_TIMED_POINTS},
                           SAMPLED_POINTS: {x: [] for x in WORD_ID_POINTS}}
        self.data_frames = {}
        self.idword_iduser_series = None

    @staticmethod
    def _load_jsons(base_folder):
        chrono = Chrono("Reading json files...")
        jsons_data = []
        files_counter = 0
        for root, dirs, files in os.walk(base_folder, True, None, False):
            for json_file in sorted(files, key=Utils.natural_keys):
                if json_file and json_file.endswith(FILE_EXTENSION):
                    json_path = os.path.realpath(os.path.join(root, json_file))
                    with open(json_path, 'r') as f:
                        jsons_data.append(json.load(f))
                    files_counter += 1
        chrono.end("read {} files".format(files_counter))
        return jsons_data

    @staticmethod
    def generate_user_identifier(data):
        return "{}_{}_{}_{}".format(data[SESSION_DATA][NAME], data[SESSION_DATA][SURNAME],
                                    data[SESSION_DATA][ID], data[SESSION_DATA][HANDWRITING])

    def _update_mappings(self, idword, single_word_data):
        assert idword not in self.idword_iduser_mapping
        assert idword not in self.idword_dataword_mapping

        self.idword_dataword_mapping[idword] = single_word_data

        iduser = self.generate_user_identifier(single_word_data)
        self.idword_iduser_mapping[idword] = iduser

        if iduser not in self.iduser_datauser_mapping:
            self.iduser_datauser_mapping[iduser] = single_word_data[SESSION_DATA]

    def get_dataframes(self):
        if self.data_frames and self.idword_iduser_series:
            return self.idword_iduser_series, self.data_frames

        chrono = Chrono("Creating dataframes...")

        for word_id, single_word_data in enumerate(self._jsons_data):
            # print("{} {} {} ".format(single_word_data[SESSION_DATA][NAME], single_word_data[SESSION_DATA][HANDWRITING], single_word_data[WORD_NUMBER]))
            self._update_mappings(word_id, single_word_data)

            for label, d in self.data_dicts.items():
                create_dict = self._from_untimed_points if label == SAMPLED_POINTS else self._from_timed_points
                self._merge_dicts(d, create_dict(word_id, single_word_data[label]))

        for label, d in self.data_dicts.items():
            self.data_frames[label] = pandas.DataFrame(d)

        self.idword_iduser_series = pandas.Series(self.idword_iduser_mapping)

        chrono.end()
        return self.idword_iduser_series, self.data_frames

    @staticmethod
    def _merge_dicts(dict1: dict, dict2: dict):
        assert set(dict1.keys()) == set(dict2.keys())
        for key in dict1.keys():
            dict1[key] += dict2[key]

    @staticmethod
    def _init_dict(labels, length):
        return {x: [None] * length for x in labels}

    @staticmethod
    def _from_timed_points(word_id, points_data):
        points_dict = JsonLoader._init_dict(WORD_ID_TIMED_POINTS, len(points_data))
        for i, point in enumerate(points_data):
            points_dict[WORD_ID][i] = word_id
            for label in TIMED_POINTS:
                points_dict[label][i] = point[label]
        return points_dict

    @staticmethod
    def _from_untimed_points(word_id, points_data):
        points_dict = JsonLoader._init_dict(WORD_ID_POINTS, sum((len(x) for x in points_data)))
        counter = 0
        for current_component, points in enumerate(points_data):
            for point in points:
                points_dict[WORD_ID][counter] = word_id
                for label in POINTS:
                    points_dict[label][counter] = point[label] if label is not COMPONENT else current_component
                counter += 1
        return points_dict
