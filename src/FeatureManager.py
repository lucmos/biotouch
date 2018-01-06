import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)

import src.DataManager as dm
from src.Chronometer import Chrono
import src.Utils as Utils
import tsfresh
import pandas
from src.Constants import *

import logging
logging.basicConfig(level=logging.ERROR)

class FeaturesManager:

    @staticmethod
    def _check_saved_pickles():
        for label in TIMED_POINTS_SERIES_TYPE:
            if not os.path.isfile(BUILD_FEATURE_PICKLE_PATH(label)):
                return False
        return True

    @staticmethod
    def extract_features_from_dataframe(dataframe: pandas.DataFrame, wordid_userid_mapping):
        return tsfresh.extract_relevant_features(dataframe, wordid_userid_mapping,
                                                 column_id=WORD_ID, column_sort=TIME, n_jobs=8)

    def __init__(self, update_data=False, update_features=False):
        update_features = update_features or update_data

        self.data_frames = {}
        self.data_features = {}

        self._load_features(update_data, update_features)

    def get_features(self):
        return self.data_features

    def get_classes(self):
        return self.data_frames[WORDID_USERID]

    def _load_features(self, update_data, update_features):
        if not update_features and FeaturesManager._check_saved_pickles():
            self._read_pickles()
        else:
            self.data_frames = dm.DataManager(update_data).get_dataframes()
            self._extract_features_from_dataframes()
            self._save_features()

    def _read_pickles(self):
        chrono = Chrono("Reading features...")
        for label in TIMED_POINTS_SERIES_TYPE:
            self.data_features[label] = pandas.read_pickle(BUILD_FEATURE_PICKLE_PATH(label))
        self.data_frames[WORDID_USERID] = pandas.read_pickle(BUILD_DATAFRAME_PICKLE_PATH(WORDID_USERID))
        chrono.end()

    def _extract_features_from_dataframes(self):
        chrono = Chrono("Extracting features...", True)
        for label in TIMED_POINTS_SERIES_TYPE:
            self.data_features[label] = self.extract_features_from_dataframe(self.data_frames[label],
                                                                             self.data_frames[WORDID_USERID])
        chrono.end()

    def _save_features(self, to_csv=True):
        Utils.save_dataframes(self.data_features, FEATURE, "Saving features...",
                              to_csv, TIMED_POINTS_SERIES_TYPE, self.data_frames[WORDID_USERID])


if __name__ == '__main__':
    FeaturesManager(update_data=True)
