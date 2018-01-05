# -*- coding: utf-8 -*-
import os
import json
import pandas
from src.Chronometer import Chrono
import src.Utils as Utils

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


BASE_FOLDER = "../res/"
BASE_GENERATED_FOLDER = "../res/generated"
BIOTOUCH_FOLDER = BASE_FOLDER + "Biotouch"

JSON_EXTENSION = ".json"
CSV_EXTENSION = ".CSV"
PICKLE_EXTENSION = ".pickle"

DATAFRAME_TYPE = "dataframe"
FEATURE_TYPE = "features"

BUILD_PATH = lambda base, file, desc, ext: os.path.join(base, file + "_" + desc + ext)

# WORDID_USERID_CSV_FILE = _path_build("wordid_userd_id" + _dataframe_csv)
# USERID_USERDATA_CSV_FILE = _path_build("userid_userdata" + _dataframe_csv)
# TOUCH_UP_POINTS_CSV_FILE = _path_build(TOUCH_UP_POINTS + _dataframe_csv)
# TOUCH_DOWN_POINTS_CSV_FILE = _path_build(TOUCH_DOWN_POINTS + _dataframe_csv)
# MOVEMENT_POINTS_CSV_FILE = _path_build(MOVEMENT_POINTS + _dataframe_csv)
# SAMPLED_POINTS_CSV_FILE = _path_build(SAMPLED_POINTS + _dataframe_csv)

WORDID_USERID_PICKLE_FILE = BUILD_PATH(BASE_GENERATED_FOLDER, "wordid_userd_id", DATAFRAME_TYPE, PICKLE_EXTENSION)
USERID_USERDATA_PICKLE_FILE = BUILD_PATH(BASE_GENERATED_FOLDER, "userid_userdata", DATAFRAME_TYPE, PICKLE_EXTENSION)
TOUCH_UP_POINTS_PICKLE_FILE = BUILD_PATH(BASE_GENERATED_FOLDER, TOUCH_UP_POINTS, DATAFRAME_TYPE, PICKLE_EXTENSION)
TOUCH_DOWN_POINTS_PICKLE_FILE = BUILD_PATH(BASE_GENERATED_FOLDER, TOUCH_DOWN_POINTS, DATAFRAME_TYPE, PICKLE_EXTENSION)
MOVEMENT_POINTS_PICKLE_FILE = BUILD_PATH(BASE_GENERATED_FOLDER, MOVEMENT_POINTS, DATAFRAME_TYPE, PICKLE_EXTENSION)
SAMPLED_POINTS_PICKLE_FILE = BUILD_PATH(BASE_GENERATED_FOLDER, SAMPLED_POINTS, DATAFRAME_TYPE, PICKLE_EXTENSION)

WORD_ID = "word_id"
USER_ID = "user_id"

# Utils

WORD_ID_POINTS = POINTS + [WORD_ID]
WORD_ID_TIMED_POINTS = TIMED_POINTS + [WORD_ID]
POINTS_SERIES_TYPE = [MOVEMENT_POINTS, TOUCH_DOWN_POINTS, TOUCH_UP_POINTS, SAMPLED_POINTS]

# *********************************************** #


class JsonLoader:
    def __init__(self, base_folder=BIOTOUCH_FOLDER):
        assert os.path.isdir(base_folder), "Insert dataset in " + base_folder

        self.base_folder = base_folder
        self._jsons_data = None

        self.idword_dataword_mapping = {}
        self.iduser_datauser_mapping = {}
        self.idword_iduser_mapping = {}

        self.data_dicts = {MOVEMENT_POINTS: {x: [] for x in WORD_ID_TIMED_POINTS},
                           TOUCH_UP_POINTS: {x: [] for x in WORD_ID_TIMED_POINTS},
                           TOUCH_DOWN_POINTS: {x: [] for x in WORD_ID_TIMED_POINTS},
                           SAMPLED_POINTS: {x: [] for x in WORD_ID_POINTS}}
        self.data_frames = {}
        self.idword_iduser_series = None

        self._initialize()

    def _initialize(self):
        self._jsons_data = JsonLoader._load_jsons(self.base_folder)
        self._initialize_dataframes()

    @staticmethod
    def _load_jsons(base_folder):
        chrono = Chrono("Reading json files...")
        jsons_data = []
        files_counter = 0
        # for i in range(10):
        for root, dirs, files in os.walk(base_folder, True, None, False):
            for json_file in sorted(files, key=Utils.natural_keys):
                if json_file and json_file.endswith(JSON_EXTENSION):
                    json_path = os.path.realpath(os.path.join(root, json_file))
                    with open(json_path, 'r') as f:
                        jsons_data.append(json.load(f))
                    files_counter += 1
        chrono.end("read {} files".format(files_counter))
        return jsons_data

    def _initialize_dataframes(self):
        chrono = Chrono("Creating dataframes...")
        for word_id, single_word_data in enumerate(self._jsons_data):
            # print("{} {} {} ".format(single_word_data[SESSION_DATA][NAME], single_word_data[SESSION_DATA][HANDWRITING], single_word_data[WORD_NUMBER]))
            self._update_mappings(word_id, single_word_data)
            for label, d in self.data_dicts.items():
                create_dict = self._from_untimed_points if label == SAMPLED_POINTS else self._from_timed_points
                Utils.merge_dicts(d, create_dict(word_id, single_word_data[label]))
        for label, d in self.data_dicts.items():
            self.data_frames[label] = pandas.DataFrame(d)
        self.idword_iduser_series = pandas.Series(self.idword_iduser_mapping)
        chrono.end()

    def _update_mappings(self, idword, single_word_data):
        assert idword not in self.idword_iduser_mapping
        assert idword not in self.idword_dataword_mapping

        self.idword_dataword_mapping[idword] = single_word_data

        iduser = self.generate_user_identifier(single_word_data)
        self.idword_iduser_mapping[idword] = iduser

        if iduser not in self.iduser_datauser_mapping:
            self.iduser_datauser_mapping[iduser] = single_word_data[SESSION_DATA]

    def _get_iduser_datauser_dataframe(self):
        d = {}
        for key, value in sorted(self.iduser_datauser_mapping.items()):
            assert isinstance(value, dict)
            temp_dict = Utils.flat_nested_dict(value)
            temp_dict[USER_ID] = [key]
            d = Utils.merge_dicts(d, Utils.make_lists_values(temp_dict)) if d else Utils.make_lists_values(temp_dict)
        return pandas.DataFrame(d).set_index(USER_ID)

    @staticmethod
    def _from_timed_points(word_id, points_data):
        points_dict = Utils.init_dict(WORD_ID_TIMED_POINTS, len(points_data))
        for i, point in enumerate(points_data):
            points_dict[WORD_ID][i] = word_id
            for label in TIMED_POINTS:
                points_dict[label][i] = point[label]
        return points_dict

    @staticmethod
    def _from_untimed_points(word_id, points_data):
        points_dict = Utils.init_dict(WORD_ID_POINTS, sum((len(x) for x in points_data)))
        counter = 0
        for current_component, points in enumerate(points_data):
            for point in points:
                points_dict[WORD_ID][counter] = word_id
                for label in POINTS:
                    points_dict[label][counter] = point[label] if label is not COMPONENT else current_component
                counter += 1
        return points_dict

    @staticmethod
    def generate_user_identifier(data):
        return "{}_{}_{}_{}".format(data[SESSION_DATA][NAME], data[SESSION_DATA][SURNAME],
                                    data[SESSION_DATA][ID], data[SESSION_DATA][HANDWRITING])

    def get_dataframes(self):
        assert self.idword_iduser_series is not None \
               and self._get_iduser_datauser_dataframe() is not None \
               and self.data_frames is not None
        return self.idword_iduser_series, self._get_iduser_datauser_dataframe(), self.data_frames

    def save_dataframes(self):
        chrono = Chrono("Saving dataframes...")
        wordid_userid, userid_userdata, frames = self.get_dataframes()

        if not os.path.isdir(BASE_GENERATED_FOLDER):
            os.makedirs(BASE_GENERATED_FOLDER)

        wordid_userid.to_pickle(WORDID_USERID_PICKLE_FILE)
        userid_userdata.to_pickle(USERID_USERDATA_PICKLE_FILE)
        frames[MOVEMENT_POINTS].to_pickle(MOVEMENT_POINTS_PICKLE_FILE)
        frames[TOUCH_UP_POINTS].to_pickle(TOUCH_UP_POINTS_PICKLE_FILE)
        frames[TOUCH_DOWN_POINTS].to_pickle(TOUCH_DOWN_POINTS_PICKLE_FILE)
        frames[SAMPLED_POINTS].to_pickle(SAMPLED_POINTS_PICKLE_FILE)

        chrono.end()


if __name__ == "__main__":
    JsonLoader().save_dataframes()
