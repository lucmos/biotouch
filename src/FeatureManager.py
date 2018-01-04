import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import src.DataManager as dm
from src.Chronometer import Chrono
import os
from tsfresh import extract_features
from tsfresh import select_features
from tsfresh.utilities.dataframe_functions import impute
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

        self.newly_wordid_useri = a
        self.newly_userid_userdata = b
        self.newly_touch_up_points = c
        self.newly_touch_down_points = d
        self.newly_movement_points = e
        self.newly_sampled_points = f


if __name__ == '__main__':
    FeaturesExtractor(False)
