import tsfresh
import pandas

import logging
import warnings

import src.DataManager as dm
import src.Chronometer as Chronom
import src.Utils as Utils

warnings.simplefilter(action='ignore', category=FutureWarning)
logging.basicConfig(level=logging.ERROR)


class FeaturesManager:

    @staticmethod
    def _check_saved_pickles(dataset_name):
        for label in Utils.TIMED_POINTS_SERIES_TYPE:
            if not Utils.os.path.isfile(Utils.BUILD_FEATURE_PICKLE_PATH(dataset_name, label)):
                return False
        return True

    @staticmethod
    def extract_features_from_dataframe(dataframe: pandas.DataFrame, wordid_userid_mapping):
        return tsfresh.extract_relevant_features(dataframe, wordid_userid_mapping,
                                                 column_id=Utils.WORD_ID, column_sort=Utils.TIME, n_jobs=3)

    def __init__(self, dataset_name, update_data=False, update_features=False):
        update_features = update_features or update_data

        self.dataset_name = dataset_name
        self.data_frames = {}
        self.data_features = {}

        self._load_features(update_data, update_features)

    def get_features(self):
        return self.data_features

    def get_classes(self):
        return self.data_frames[Utils.WORDID_USERID]

    def get_classes_data(self):
        return self.data_frames[Utils.USERID_USERDATA]

    def _load_features(self, update_data, update_features):
        self.data_frames = dm.DataManager(self.dataset_name, update_data).get_dataframes()
        if not update_features and FeaturesManager._check_saved_pickles(self.dataset_name):
            self._read_pickles()
        else:
            self._extract_features_from_dataframes()
            self._save_features()

    def _read_pickles(self):
        chrono = Chronom.Chrono("Reading features...")
        for label in Utils.TIMED_POINTS_SERIES_TYPE:
            self.data_features[label] = pandas.read_pickle(Utils.BUILD_FEATURE_PICKLE_PATH(self.dataset_name, label))
        chrono.end()

    def _extract_features_from_dataframes(self):
        for label in Utils.TIMED_POINTS_SERIES_TYPE:
            chrono = Chronom.Chrono("Extracting features from {}...".format(label), True)
            self.data_features[label] = self.extract_features_from_dataframe(self.data_frames[label],
                                                                             self.data_frames[Utils.WORDID_USERID])
            chrono.end()

    def _save_features(self, to_csv=True):
        Utils.save_dataframes(self.dataset_name, self.data_features, Utils.FEATURE, "Saving features...",
                              to_csv, Utils.TIMED_POINTS_SERIES_TYPE, self.data_frames[Utils.WORDID_USERID])


if __name__ == '__main__':
    FeaturesManager(Utils.DATASET_NAME_0, update_data=True, update_features=True)
