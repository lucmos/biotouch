# -*- coding: utf-8 -*-
import os
import json
import pandas
from src.Chronometer import Chrono
import src.Utils as Utils

WORDID_USERID_MAP = "wordid_userid_map"
USERID_USERDATA_MAP = "userid_userdata_map"
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
CSV_EXTENSION = ".csv"
PICKLE_EXTENSION = ".pickle"

DATAFRAME_TYPE = "dataframe"
FEATURE_TYPE = "features"

BUILD_PATH = lambda base, file, desc, ext: os.path.join(base, file + "_" + desc + ext)

BUILD_DATAFRAME_PICKLE_PATH = lambda file: os.path.join(BASE_GENERATED_FOLDER, file + "_" + DATAFRAME_TYPE + PICKLE_EXTENSION)
BUILD_DATAFRAME_CSV_PATH = lambda file: os.path.join(BASE_GENERATED_FOLDER, file + "_" + DATAFRAME_TYPE + CSV_EXTENSION)

BUILD_FEATURE_PICKLE_PATH = lambda file: os.path.join(BASE_GENERATED_FOLDER, file + "_" + FEATURE_TYPE + PICKLE_EXTENSION)
BUILD_FEATURE_CSV_PATH = lambda file: os.path.join(BASE_GENERATED_FOLDER, file + "_" + FEATURE_TYPE + CSV_EXTENSION)
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
TIMED_POINTS_SERIES_TYPE = [MOVEMENT_POINTS, TOUCH_DOWN_POINTS, TOUCH_UP_POINTS]
DATAFRAMES = [WORDID_USERID_MAP, USERID_USERDATA_MAP] + POINTS_SERIES_TYPE


# *********************************************** #


class DataManager:
    @staticmethod
    def _dict_of_list_from_timed_points(word_id, _, points_data):
        points_dict = Utils.init_dict(WORD_ID_TIMED_POINTS, len(points_data))
        for i, point in enumerate(points_data):
            points_dict[WORD_ID][i] = word_id
            for label in TIMED_POINTS:
                points_dict[label][i] = point[label]
        return points_dict

    @staticmethod
    def _dict_of_list_from_untimed_points(word_id, _, points_data):
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
    def _dataframe_from_nested_dict(initialdict, base_label = USER_ID):
        d = {}
        for key, value in sorted(initialdict.items()):
            assert isinstance(value, dict)
            temp_dict = Utils.flat_nested_dict(value)
            temp_dict[base_label] = [key]
            d = Utils.merge_dicts(d, Utils.make_lists_values(temp_dict)) if d else Utils.make_lists_values(temp_dict)
        return pandas.DataFrame(d).set_index(USER_ID)

    @staticmethod
    def _check_saved_pickles():
        for label in DATAFRAMES:
            if not os.path.isfile(BUILD_DATAFRAME_PICKLE_PATH(label)):
                return False
        return True

    @staticmethod
    def get_userid(data):
        norm = lambda t: "".join(t.lower().split())
        return "{}_{}_{}_{}".format(norm(data[SESSION_DATA][NAME]), norm(data[SESSION_DATA][SURNAME]),
                                    data[SESSION_DATA][ID], data[SESSION_DATA][HANDWRITING])

    def __init__(self, update_data=False, base_folder=BIOTOUCH_FOLDER):
        assert os.path.isdir(base_folder), "Insert dataset in " + base_folder

        self.base_folder = base_folder
        self._jsons_data = []

        # useful for test purposes
        self.idword_dataword_mapping = {}

        self.data_dicts = {WORDID_USERID_MAP: {},
                           USERID_USERDATA_MAP: {},
                           MOVEMENT_POINTS: {x: [] for x in WORD_ID_TIMED_POINTS},
                           TOUCH_UP_POINTS: {x: [] for x in WORD_ID_TIMED_POINTS},
                           TOUCH_DOWN_POINTS: {x: [] for x in WORD_ID_TIMED_POINTS},
                           SAMPLED_POINTS: {x: [] for x in WORD_ID_POINTS}}

        self.data_frames = {WORDID_USERID_MAP: None,
                            USERID_USERDATA_MAP: None,
                            MOVEMENT_POINTS: None,
                            TOUCH_UP_POINTS: None,
                            TOUCH_DOWN_POINTS: None,
                            SAMPLED_POINTS: None}

        self.data_to_dict_funs = {WORDID_USERID_MAP: None,
                                  USERID_USERDATA_MAP: None,
                                  MOVEMENT_POINTS: DataManager._dict_of_list_from_timed_points,
                                  TOUCH_UP_POINTS: DataManager._dict_of_list_from_timed_points,
                                  TOUCH_DOWN_POINTS: DataManager._dict_of_list_from_timed_points,
                                  SAMPLED_POINTS: DataManager._dict_of_list_from_untimed_points}

        self.dict_to_frames_funs = {WORDID_USERID_MAP: pandas.Series,
                                    USERID_USERDATA_MAP: DataManager._dataframe_from_nested_dict,
                                    MOVEMENT_POINTS: pandas.DataFrame,
                                    TOUCH_UP_POINTS: pandas.DataFrame,
                                    TOUCH_DOWN_POINTS: pandas.DataFrame,
                                    SAMPLED_POINTS: pandas.DataFrame}

        self._load_dataframes(update_data)

    def get_dataframes(self):
        assert self.data_frames
        for x, v in self.data_frames.items():
            assert v is not None
        return self.data_frames

    def get_datadicts(self):
        assert self.data_dicts, "Rember to force a regen first"
        for x, v in self.data_dicts.items():
            assert v, "Rember to force a regen first"
        return self.data_dicts

    def _save_dataframes(self, to_csv=True):
        chrono = Chrono("Saving dataframes...")
        if not os.path.isdir(BASE_GENERATED_FOLDER):
            os.makedirs(BASE_GENERATED_FOLDER)

        for label, v in self.get_dataframes().items():
            v.to_pickle(BUILD_DATAFRAME_PICKLE_PATH(label))
            if to_csv:
                v.to_csv(BUILD_DATAFRAME_CSV_PATH(label), sep=";", decimal=",")
        chrono.end()

    def _load_jsons(self):
        chrono = Chrono("Reading json files...")
        files_counter = 0
        for root, dirs, files in os.walk(self.base_folder, True, None, False):
            for json_file in sorted(files, key=Utils.natural_keys):
                if json_file and json_file.endswith(JSON_EXTENSION):
                    json_path = os.path.realpath(os.path.join(root, json_file))
                    with open(json_path, 'r') as f:
                        self._jsons_data.append(json.load(f))
                    files_counter += 1
        chrono.end("read {} files".format(files_counter))

    def _load_dataframes(self, update):
        if not update and DataManager._check_saved_pickles():
            self._read_pickles()
        else:
            self._load_jsons()
            self._create_dataframes()
            self._save_dataframes()

    def _read_pickles(self):
        chrono = Chrono("Reading dataframes...")
        for label in DATAFRAMES:
            self.data_frames[label] = pandas.read_pickle(BUILD_DATAFRAME_PICKLE_PATH(label))
        chrono.end()

    def _create_dataframes(self):
        assert self._jsons_data
        chrono = Chrono("Creating dataframes...")
        for word_id, single_word_data in enumerate(self._jsons_data):
            self.idword_dataword_mapping[word_id] = single_word_data

            iduser = self.get_userid(single_word_data)
            self.data_dicts[WORDID_USERID_MAP][word_id] = iduser
            if iduser not in self.data_dicts[USERID_USERDATA_MAP]:
                self.data_dicts[USERID_USERDATA_MAP][iduser] = single_word_data[SESSION_DATA]

            for label in POINTS_SERIES_TYPE:
                Utils.merge_dicts(self.data_dicts[label], self.data_to_dict_funs[label](word_id, iduser,
                                                                                        single_word_data[label]))

        for label, d in self.data_dicts.items():
            self.data_frames[label] = self.dict_to_frames_funs[label](d)
        chrono.end()


if __name__ == "__main__":
    DataManager(update_data=True)
