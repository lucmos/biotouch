# -*- coding: utf-8 -*-
import json
import pandas
from src.Chronometer import Chrono
import src.Utils as Utils
from src.Constants import *

DATAFRAME_FROM_JSON = [WORDID_USERID, USERID_USERDATA] + INITIAL_POINTS_SERIES_TYPE
DATAFRAMES = [WORDID_USERID, USERID_USERDATA] + POINTS_SERIES_TYPE


class DataManager:
    @staticmethod
    def _dict_of_list_from_timed_points(word_id, _, points_data):
        points_dict = Utils.init_dict(TIMED_POINTS_WITH_WORD_ID, len(points_data))
        for i, point in enumerate(points_data):
            points_dict[WORD_ID][i] = word_id
            for label in TIMED_POINTS:
                points_dict[label][i] = point[label]
        return points_dict

    @staticmethod
    def _dict_of_list_from_untimed_points(word_id, _, points_data):
        points_dict = Utils.init_dict(POINTS_WITH_WORD_ID, sum((len(x) for x in points_data)))
        counter = 0
        for current_component, points in enumerate(points_data):
            for point in points:
                points_dict[WORD_ID][counter] = word_id
                for label in POINTS:
                    points_dict[label][counter] = point[label] if label is not COMPONENT else current_component
                counter += 1
        return points_dict

    @staticmethod
    def _dataframe_from_nested_dict(initialdict, base_label=USER_ID):
        d = {}
        for key, value in sorted(initialdict.items()):
            assert isinstance(value, dict)
            temp_dict = Utils.flat_nested_dict(value)
            temp_dict[base_label] = [key]
            d = Utils.merge_dicts(d, Utils.make_lists_values(temp_dict)) if d else Utils.make_lists_values(temp_dict)
        return pandas.DataFrame(d).set_index(USER_ID)

    @staticmethod
    def _check_saved_pickles(dataset_name):
        for label in DATAFRAMES:
            if not os.path.isfile(BUILD_DATAFRAME_PICKLE_PATH(dataset_name, label)):
                return False
        return True

    @staticmethod
    def get_userid(data):
        norm = lambda t: "".join(t.lower().split())
        return "{}_{}_{}_{}_{}".format(norm(data[SESSION_DATA][NAME]),
                                       norm(data[SESSION_DATA][SURNAME]),
                                       norm(data[SESSION_DATA][DEVICE_DATA][DEVICE_MODEL]),
                                       data[SESSION_DATA][ID],
                                       data[SESSION_DATA][HANDWRITING])

    def __init__(self, dataset_name, update_data=False):
        self.dataset_name = dataset_name

        self._jsons_data = []

        # useful for test purposes
        self._idword_dataword_mapping = {}

        self._data_dicts = {WORDID_USERID: {},
                            USERID_USERDATA: {},
                            MOVEMENT_POINTS: {x: [] for x in TIMED_POINTS_WITH_WORD_ID},
                            TOUCH_UP_POINTS: {x: [] for x in TIMED_POINTS_WITH_WORD_ID},
                            TOUCH_DOWN_POINTS: {x: [] for x in TIMED_POINTS_WITH_WORD_ID},
                            SAMPLED_POINTS: {x: [] for x in POINTS_WITH_WORD_ID}}

        self.data_frames = {WORDID_USERID: None,
                            USERID_USERDATA: None,
                            MOVEMENT_POINTS: None,
                            TOUCH_UP_POINTS: None,
                            TOUCH_DOWN_POINTS: None,
                            SAMPLED_POINTS: None,

                            X_SHIFTED_MOVEMENT_POINTS: None,
                            X_SHIFTED_TOUCH_DOWN_POINTS: None,
                            X_SHIFTED_TOUCH_UP_POINTS: None,
                            X_SHIFTED_SAMPLED_POINTS: None,

                            Y_SHIFTED_MOVEMENT_POINTS: None,
                            Y_SHIFTED_TOUCH_DOWN_POINTS: None,
                            Y_SHIFTED_TOUCH_UP_POINTS: None,
                            Y_SHIFTED_SAMPLED_POINTS: None,

                            XY_SHIFTED_MOVEMENT_POINTS: None,
                            XY_SHIFTED_TOUCH_DOWN_POINTS: None,
                            XY_SHIFTED_TOUCH_UP_POINTS: None,
                            XY_SHIFTED_SAMPLED_POINTS: None}

        self._data_to_dict_funs = {WORDID_USERID: None,
                                   USERID_USERDATA: None,
                                   MOVEMENT_POINTS: DataManager._dict_of_list_from_timed_points,
                                   TOUCH_UP_POINTS: DataManager._dict_of_list_from_timed_points,
                                   TOUCH_DOWN_POINTS: DataManager._dict_of_list_from_timed_points,
                                   SAMPLED_POINTS: DataManager._dict_of_list_from_untimed_points}

        self._dict_to_frames_funs = {WORDID_USERID: lambda x: pandas.Series(x, name=USER_ID),
                                     USERID_USERDATA: DataManager._dataframe_from_nested_dict,
                                     MOVEMENT_POINTS: pandas.DataFrame,
                                     TOUCH_UP_POINTS: pandas.DataFrame,
                                     TOUCH_DOWN_POINTS: pandas.DataFrame,
                                     SAMPLED_POINTS: pandas.DataFrame}

        # {word_id: (minX, minY) }
        self.shift_offsets = {}

        self._load_dataframes(update_data)

    def get_dataframes(self):
        assert self.data_frames
        for x, v in self.data_frames.items():
            assert v is not None
        return self.data_frames

    def _load_dataframes(self, update):
        if not update and DataManager._check_saved_pickles(self.dataset_name):
            self._read_pickles()
        else:
            self._load_jsons()
            self._create_dataframes()
            self._shift()
            self._save_dataframes()

    def _save_dataframes(self, to_csv=True):
        Utils.save_dataframes(self.dataset_name, self.get_dataframes(), DATAFRAME, "Saving dataframes...",
                              to_csv, POINTS_SERIES_TYPE, self.get_dataframes()[WORDID_USERID])

    def _load_jsons(self):
        assert os.path.isdir(BUILD_DATASET_FOLDER(
            self.dataset_name)), "Insert the dataset \"" + self.dataset_name + "\" in: " + BASE_FOLDER

        chrono = Chrono("Reading json files...")
        files_counter = 0
        for root, dirs, files in os.walk(BUILD_DATASET_FOLDER(self.dataset_name), True, None, False):
            for json_file in sorted(files, key=Utils.natural_keys):
                if json_file and json_file.endswith(JSON_EXTENSION):
                    json_path = os.path.realpath(os.path.join(root, json_file))
                    with open(json_path, 'r') as f:
                        self._jsons_data.append(json.load(f))
                    files_counter += 1
        chrono.end("read {} files".format(files_counter))

    def _read_pickles(self):
        chrono = Chrono("Reading dataframes...")
        for label in DATAFRAMES:
            self.data_frames[label] = pandas.read_pickle(BUILD_DATAFRAME_PICKLE_PATH(self.dataset_name, label))
        chrono.end()

    def _create_dataframes(self):
        assert self._jsons_data
        chrono = Chrono("Creating dataframes...")
        for word_id, single_word_data in enumerate(self._jsons_data):
            self._idword_dataword_mapping[word_id] = single_word_data

            iduser = self.get_userid(single_word_data)
            self._data_dicts[WORDID_USERID][word_id] = iduser
            if iduser not in self._data_dicts[USERID_USERDATA]:
                self._data_dicts[USERID_USERDATA][iduser] = single_word_data[SESSION_DATA]

            for label in INITIAL_POINTS_SERIES_TYPE:
                Utils.merge_dicts(self._data_dicts[label], self._data_to_dict_funs[label](word_id, iduser,
                                                                                          single_word_data[label]))

        for label, d in self._data_dicts.items():
            self.data_frames[label] = self._dict_to_frames_funs[label](d)
        chrono.end()

    def _group_compute_offsets(self, group):
        minX = group[X].min()
        minY = group[Y].min()
        self.shift_offsets[group[WORD_ID].iloc[0]] = (minX, minY)

    def _group_shift_x(self, group):
        m = self.shift_offsets[group[WORD_ID].iloc[0]][0]
        group[X] = group[X] - m
        return group

    def _group_shift_y(self, group):
        m = self.shift_offsets[group[WORD_ID].iloc[0]][1]
        group[Y] = group[Y] - m
        return group

    def _group_shift_xy(self, group):
        return self._group_shift_x(self._group_shift_y(group))

    def _shift(self):
        chrono = Chrono("Shifting dataframes...")
        self.data_frames[MOVEMENT_POINTS].groupby(WORD_ID).apply(self._group_compute_offsets)

        f = {X: self._group_shift_x,
             Y: self._group_shift_y,
             XY: self._group_shift_xy}

        for l in INITIAL_POINTS_SERIES_TYPE:
            for dir in [X, Y, XY]:
                self.data_frames[GET_SHIFTED_POINTS_NAME(dir, l)] = self.data_frames[l].groupby(WORD_ID).apply(f[dir])
        chrono.end()

     # todo: implementa plotting		     # todo: implementa plotting
     # def print(self):		     # def print(self):
     #     plt.interactive(False)		     #     plt.interactive(False)
     #     d['y'] *= -1		     #     d['y'] *= -1
     #		     #
     #     d[d.word_id == 0][["x", "y"]].plot(x="x", y="y", kind="scatter")		     #     d[d.word_id == 0][["x", "y"]].plot(x="x", y="y", kind="scatter")
     #     plt.axes().set_aspect('equal', 'datalim')		     #     plt.axes().set_aspect('equal', 'datalim')
     #     plt.show()

if __name__ == "__main__":
    DataManager(DATASET_NAME_0, update_data=True)
