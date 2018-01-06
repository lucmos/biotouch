import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)

import src.DataManager as dm
from src.Chronometer import Chrono
import os
import tsfresh
import pandas


class FeaturesExtractor:

    @staticmethod
    def extract_features_from_dataframe(dataframe: pandas.DataFrame, wordid_userid_mapping):
        return tsfresh.extract_relevant_features(dataframe, wordid_userid_mapping,
                                                 column_id=dm.WORD_ID, column_sort=dm.TIME, n_jobs=8)

    def __init__(self, update_data=False):
        self.data_frames = dm.DataManager(update_data).get_dataframes()
        self.data_features = {}
        self.extract_features_from_dataframes()

    def extract_features_from_dataframes(self):
        chrono = Chrono("Extracting features...")
        for label in dm.TIMED_POINTS_SERIES_TYPE:
            self.data_features[label] = self.extract_features_from_dataframe(self.data_frames[label],
                                                                             self.data_frames[dm.WORDID_USERID_MAP])
        chrono.end()

    def save_features(self, to_csv=True):
        chrono = Chrono("Saving features...")
        for label, features in self.data_features.items():
            features.to_pickle(dm.BUILD_FEATURE_PICKLE_PATH(label))
            if to_csv:
                features_id = features.copy()
                features_id[dm.USER_ID] = self.data_frames[dm.WORDID_USERID_MAP]
                features_id.to_csv( dm.BUILD_FEATURE_CSV_PATH(label), decimal=",", sep=";")
        chrono.end()


if __name__ == '__main__':
    FeaturesExtractor().save_features()
