import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)

import src.DataManager as dm
from src.Chronometer import Chrono
import os
import tsfresh
import pandas


class FeaturesExtractor():

    @staticmethod
    def _read_pickles():
        chrono = Chrono("Reading dataframes...")
        a = pandas.read_pickle(dm.WORDID_USERID_PICKLE_FILE)
        b = pandas.read_pickle(dm.USERID_USERDATA_PICKLE_FILE)
        c = pandas.read_pickle(dm.TOUCH_UP_POINTS_PICKLE_FILE)
        d = pandas.read_pickle(dm.TOUCH_DOWN_POINTS_PICKLE_FILE)
        e = pandas.read_pickle(dm.MOVEMENT_POINTS_PICKLE_FILE)
        f = pandas.read_pickle(dm.SAMPLED_POINTS_PICKLE_FILE)
        chrono.end()
        return a, b, c, d, e, f

    @staticmethod
    def _regen_dataframes():
        loader = dm.JsonLoader()
        loader.save_dataframes()
        a, b, frames = loader.get_dataframes()
        c = frames[dm.TOUCH_UP_POINTS]
        d = frames[dm.TOUCH_DOWN_POINTS]
        e = frames[dm.MOVEMENT_POINTS]
        f = frames[dm.SAMPLED_POINTS]
        return a, b, c, d, e, f

    def __init__(self, update=False):
        if (not update
                and os.path.isfile(dm.WORDID_USERID_PICKLE_FILE)
                and os.path.isfile(dm.USERID_USERDATA_PICKLE_FILE)
                and os.path.isfile(dm.TOUCH_UP_POINTS_PICKLE_FILE)
                and os.path.isfile(dm.TOUCH_DOWN_POINTS_PICKLE_FILE)
                and os.path.isfile(dm.MOVEMENT_POINTS_PICKLE_FILE)
                and os.path.isfile(dm.SAMPLED_POINTS_PICKLE_FILE)):
            a, b, c, d, e, f = FeaturesExtractor._read_pickles()
        else:
            a, b, c, d, e, f = FeaturesExtractor._regen_dataframes()

        self.wordid_userid = a
        self.userid_userdata = b

        self.data_dataframes = {dm.TOUCH_UP_POINTS: c,
                                dm.TOUCH_DOWN_POINTS: d,
                                dm.MOVEMENT_POINTS: e,
                                dm.SAMPLED_POINTS: f}
        self.data_features = {}
        self.extract_features_from_dataframes()

    @staticmethod
    def extract_features_from_dataframe(dataframe: pandas.DataFrame, wordid_userid_mapping):
        return tsfresh.extract_relevant_features(dataframe, wordid_userid_mapping,
                                                 column_id=dm.WORD_ID, column_sort=dm.TIME, n_jobs=8)

    def extract_features_from_dataframes(self):
        chrono = Chrono("Extracting features...")
        for points_type, points in self.data_dataframes.items():
            if points_type == dm.SAMPLED_POINTS:
                continue
            self.data_features[points_type] = self.extract_features_from_dataframe(points, self.wordid_userid)
        chrono.end()

    def save_features(self, save_csv=True):
        chrono = Chrono("Saving features...")
        for label, features in self.data_features.items():
            features.to_pickle( dm.BUILD_PATH(dm.BASE_GENERATED_FOLDER, label, dm.FEATURE_TYPE, dm.PICKLE_EXTENSION))
            features_id = features.copy()
            features_id[dm.USER_ID] = self.wordid_userid
            features_id.to_csv( dm.BUILD_PATH(dm.BASE_GENERATED_FOLDER, label, dm.FEATURE_TYPE, dm.CSV_EXTENSION), decimal=",", sep=";")
        chrono.end()



if __name__ == '__main__':
    FeaturesExtractor(False).save_features()
