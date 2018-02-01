# -*- coding: utf-8 -*-
import json
import random
import pandas

import src.Chronometer as Chronom
import src.Plotter as Plot
import src.Utils as Utils


DATAFRAME_FROM_JSON = [Utils.WORDID_USERID, Utils.USERID_USERDATA] + Utils.INITIAL_POINTS_SERIES_TYPE
DATAFRAMES = [Utils.WORDID_USERID, Utils.USERID_USERDATA] + Utils.POINTS_SERIES_TYPE


class DataManager:
    @staticmethod
    def _dict_of_list_from_timed_points(word_id, _, points_data):
        points_dict = Utils.init_dict(Utils.TIMED_POINTS_WITH_WORD_ID, len(points_data))
        for i, point in enumerate(points_data):
            points_dict[Utils.WORD_ID][i] = word_id
            for label in Utils.TIMED_POINTS:
                points_dict[label][i] = point[label]
        return points_dict

    @staticmethod
    def _dict_of_list_from_untimed_points(word_id, _, points_data):
        points_dict = Utils.init_dict(Utils.POINTS_WITH_WORD_ID, sum((len(x) for x in points_data)))
        counter = 0
        for current_component, points in enumerate(points_data):
            for point in points:
                points_dict[Utils.WORD_ID][counter] = word_id
                for label in Utils.POINTS:
                    points_dict[label][counter] = point[label] if label is not Utils.COMPONENT else current_component
                counter += 1
        return points_dict

    @staticmethod
    def _dataframe_from_nested_dict(initialdict, base_label=Utils.USER_ID):
        d = {}
        for key, value in sorted(initialdict.items()):
            assert isinstance(value, dict)
            temp_dict = Utils.flat_nested_dict(value)
            temp_dict[base_label] = [key]
            d = Utils.merge_dicts(d, Utils.make_lists_values(temp_dict)) if d else Utils.make_lists_values(temp_dict)
        return pandas.DataFrame(d).set_index(Utils.USER_ID)

    @staticmethod
    def _check_saved_pickles(dataset_name):
        for label in DATAFRAMES:
            if not Utils.os.path.isfile(Utils.BUILD_DATAFRAME_PICKLE_PATH(dataset_name, label)):
                return False
        return True


    @staticmethod
    def get_userid(data):
        return "{}_{}_{}_{}_{}".format(Utils.uglify(data[Utils.SESSION_DATA][Utils.NAME]),
                                       Utils.uglify(data[Utils.SESSION_DATA][Utils.SURNAME]),
                                       Utils.uglify(data[Utils.SESSION_DATA][Utils.DEVICE_DATA][Utils.DEVICE_MODEL]),
                                       data[Utils.SESSION_DATA][Utils.ID],
                                       data[Utils.SESSION_DATA][Utils.HANDWRITING])

    def __init__(self, dataset_name, update_data=False):
        self.dataset_name = dataset_name

        self._jsons_data = []

        # useful for test purposes
        self._idword_dataword_mapping = {}

        self._data_dicts = {Utils.WORDID_USERID: {},
                            Utils.USERID_USERDATA: {},
                            Utils.MOVEMENT_POINTS: {x: [] for x in Utils.TIMED_POINTS_WITH_WORD_ID},
                            Utils.TOUCH_UP_POINTS: {x: [] for x in Utils.TIMED_POINTS_WITH_WORD_ID},
                            Utils.TOUCH_DOWN_POINTS: {x: [] for x in Utils.TIMED_POINTS_WITH_WORD_ID},
                            Utils.SAMPLED_POINTS: {x: [] for x in Utils.POINTS_WITH_WORD_ID}}

        self.data_frames = {Utils.WORDID_USERID: None,
                            Utils.USERID_USERDATA: None,
                            Utils.MOVEMENT_POINTS: None,
                            Utils.TOUCH_UP_POINTS: None,
                            Utils.TOUCH_DOWN_POINTS: None,
                            Utils.SAMPLED_POINTS: None,

                            # Utils.X_SHIFTED_MOVEMENT_POINTS: None,
                            # Utils.X_SHIFTED_TOUCH_DOWN_POINTS: None,
                            # Utils.X_SHIFTED_TOUCH_UP_POINTS: None,
                            # Utils.X_SHIFTED_SAMPLED_POINTS: None,
                            #
                            # Utils.Y_SHIFTED_MOVEMENT_POINTS: None,
                            # Utils.Y_SHIFTED_TOUCH_DOWN_POINTS: None,
                            # Utils.Y_SHIFTED_TOUCH_UP_POINTS: None,
                            # Utils.Y_SHIFTED_SAMPLED_POINTS: None,

                            Utils.XY_SHIFTED_MOVEMENT_POINTS: None,
                            Utils.XY_SHIFTED_TOUCH_DOWN_POINTS: None,
                            Utils.XY_SHIFTED_TOUCH_UP_POINTS: None,
                            Utils.XY_SHIFTED_SAMPLED_POINTS: None}

        self._data_to_dict_funs = {Utils.WORDID_USERID: None,
                                   Utils.USERID_USERDATA: None,
                                   Utils.MOVEMENT_POINTS: DataManager._dict_of_list_from_timed_points,
                                   Utils.TOUCH_UP_POINTS: DataManager._dict_of_list_from_timed_points,
                                   Utils.TOUCH_DOWN_POINTS: DataManager._dict_of_list_from_timed_points,
                                   Utils.SAMPLED_POINTS: DataManager._dict_of_list_from_untimed_points}

        self._dict_to_frames_funs = {Utils.WORDID_USERID: lambda x: pandas.Series(x, name=Utils.USER_ID),
                                     Utils.USERID_USERDATA: DataManager._dataframe_from_nested_dict,
                                     Utils.MOVEMENT_POINTS: pandas.DataFrame,
                                     Utils.TOUCH_UP_POINTS: pandas.DataFrame,
                                     Utils.TOUCH_DOWN_POINTS: pandas.DataFrame,
                                     Utils.SAMPLED_POINTS: pandas.DataFrame}

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
            self._generate_dataframes()
            self._save_dataframes()
            self._generate_example_charts()

    def _generate_dataframes(self):
        self._load_jsons()
        self._create_dataframes()
        self._shift()

    def _load_jsons(self):
        assert Utils.os.path.isdir(Utils.BUILD_DATASET_FOLDER(
            self.dataset_name)), "Insert the dataset \"" + self.dataset_name + "\" in: " + Utils.BASE_FOLDER

        chrono = Chronom.Chrono("Reading json files...")
        files_counter = 0
        for root, dirs, files in Utils.os.walk(Utils.BUILD_DATASET_FOLDER(self.dataset_name), True, None, False):
            for json_file in sorted(files, key=Utils.natural_keys):
                if json_file and json_file.endswith(Utils.JSON_EXTENSION):
                    json_path = Utils.os.path.realpath(Utils.os.path.join(root, json_file))
                    with open(json_path, 'r') as f:
                        self._jsons_data.append(json.load(f))
                    files_counter += 1
        chrono.end("read {} files".format(files_counter))

    def _create_dataframes(self):
        assert self._jsons_data
        chrono = Chronom.Chrono("Creating dataframes...")
        for word_id, single_word_data in enumerate(self._jsons_data):
            self._idword_dataword_mapping[word_id] = single_word_data

            iduser = self.get_userid(single_word_data)
            self._data_dicts[Utils.WORDID_USERID][word_id] = iduser
            if iduser not in self._data_dicts[Utils.USERID_USERDATA]:
                self._data_dicts[Utils.USERID_USERDATA][iduser] = single_word_data[Utils.SESSION_DATA]

            for label in Utils.INITIAL_POINTS_SERIES_TYPE:
                Utils.merge_dicts(self._data_dicts[label], self._data_to_dict_funs[label](word_id, iduser,
                                                                                                                  single_word_data[label]))

        for label, d in self._data_dicts.items():
            self.data_frames[label] = self._dict_to_frames_funs[label](d)

        self.data_frames[Utils.USERID_USERDATA][Utils.NAME] = self.data_frames[Utils.USERID_USERDATA][Utils.NAME].str.lower()
        self.data_frames[Utils.USERID_USERDATA][Utils.SURNAME] = self.data_frames[Utils.USERID_USERDATA][Utils.SURNAME].str.lower()
        chrono.end()

    def _group_compute_offsets(self, group):
        minX = group[Utils.X].min()
        minY = group[Utils.Y].min()
        self.shift_offsets[group[Utils.WORD_ID].iloc[0]] = (minX, minY)

    def _group_shift_x(self, group):
        m = self.shift_offsets[group[Utils.WORD_ID].iloc[0]][0]
        group[Utils.X] = group[Utils.X] - m
        return group

    def _group_shift_y(self, group):
        m = self.shift_offsets[group[Utils.WORD_ID].iloc[0]][1]
        group[Utils.Y] = group[Utils.Y] - m
        return group

    def _group_shift_xy(self, group):
        return self._group_shift_x(self._group_shift_y(group))

    def _shift(self):
        chrono = Chronom.Chrono("Shifting dataframes...")
        self.data_frames[Utils.MOVEMENT_POINTS].groupby(Utils.WORD_ID).apply(self._group_compute_offsets)

        f = {Utils.X: self._group_shift_x,
             Utils.Y: self._group_shift_y,
             Utils.XY: self._group_shift_xy}

        for l in Utils.INITIAL_POINTS_SERIES_TYPE:
            for dir in [Utils.X, Utils.Y, Utils.XY]:
                self.data_frames[Utils.GET_SHIFTED_POINTS_NAME(dir, l)] = self.data_frames[l].groupby(Utils.WORD_ID).apply(f[dir])
        chrono.end()

    def _read_pickles(self):
        chrono = Chronom.Chrono("Reading dataframes...")
        for label in DATAFRAMES:
            self.data_frames[label] = pandas.read_pickle(Utils.BUILD_DATAFRAME_PICKLE_PATH(self.dataset_name, label))
        chrono.end()

    def _save_dataframes(self, to_csv=True):
        Utils.save_dataframes(self.dataset_name, self.get_dataframes(), Utils.DATAFRAME, "Saving dataframes...",
                              to_csv, Utils.POINTS_SERIES_TYPE, self.get_dataframes()[Utils.WORDID_USERID])

    def _generate_example_charts(self):
        examples = [
            {Utils.NAME:"Rita", Utils.SURNAME:"Battilocchi", Utils.WORD_NUMBER:5, Utils.HANDWRITING: Utils.ITALIC},
            {Utils.NAME: "Alessio", Utils.SURNAME: "Mecca", Utils.WORD_NUMBER: 13, Utils.HANDWRITING: Utils.BLOCK_LETTER}

        ]
        dataframes = self.get_dataframes()
        for ex in examples:
            Plot.GifCreator(      Utils.DATASET_NAME_0, dataframes, dataframes[Utils.WORDID_USERID], dataframes[Utils.USERID_USERDATA], name=ex.get(Utils.NAME), surname=ex.get(Utils.SURNAME), word_number=ex.get(Utils.WORD_NUMBER), handwriting=ex.get(Utils.HANDWRITING))
            p = Plot.ChartCreator(Utils.DATASET_NAME_0, dataframes, dataframes[Utils.WORDID_USERID], dataframes[Utils.USERID_USERDATA], name=ex.get(Utils.NAME), surname=ex.get(Utils.SURNAME), word_number=ex.get(Utils.WORD_NUMBER), handwriting=ex.get(Utils.HANDWRITING))
            p.plot2dataframe()
            p.plot3dataframe()
            Plot.ChartCreator(Utils.DATASET_NAME_0, dataframes, dataframes[Utils.WORDID_USERID], dataframes[Utils.USERID_USERDATA],  name=ex.get(Utils.NAME), surname=ex.get(Utils.SURNAME), word_number=ex.get(Utils.WORD_NUMBER), handwriting=ex.get(Utils.HANDWRITING), label=Utils.XY_SHIFTED_MOVEMENT_POINTS).plot2dataframe()



if __name__ == "__main__":
    d = DataManager(Utils.DATASET_NAME_0, update_data=False)

    # a = Utils.get_wordidfrom_wordnumber_name_surname(d[Utils.WORDID_USERID], d[Utils.USERID_USERDATA], "Rita", "Battilocchi" , Utils.BLOCK_LETTER, 31)
    # print(Utils.get_infos(d[Utils.WORDID_USERID], d[Utils.USERID_USERDATA], a))
    d._generate_example_charts()
