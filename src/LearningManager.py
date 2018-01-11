import random
import pandas
from pandas.util.testing import assert_series_equal

import warnings
import logging

import sklearn.exceptions
from sklearn import preprocessing
from sklearn.metrics import *
from sklearn.model_selection import train_test_split
from sklearn.multiclass import OneVsRestClassifier
from sklearn.preprocessing import *
from sklearn.svm import SVC
from sklearn.model_selection import GridSearchCV

import src.FeatureManager as fm
import src.Utils as Utils

logging.basicConfig(level=logging.ERROR)

warnings.filterwarnings("ignore", category=sklearn.exceptions.UndefinedMetricWarning)


def filter_dataframe_by_handwriting(dataframe, classes, user_data, handwriting):
    temp = dataframe.join(classes).join(user_data[Utils.HANDWRITING], on=Utils.USER_ID).drop(Utils.USER_ID, axis=1)
    return temp[temp[Utils.HANDWRITING] == handwriting].drop(Utils.HANDWRITING, axis=1)


def filter_classes_by_handwriting(classes, user_data, handwriting):
    temp = pandas.DataFrame(classes).join(user_data[Utils.HANDWRITING], on=Utils.USER_ID)
    return temp[temp[Utils.HANDWRITING] == handwriting].drop(Utils.HANDWRITING, axis=1).squeeze()


def filter_by_handwriting(dataframe, classes, user_data, handwriting):
    return (filter_dataframe_by_handwriting(dataframe, classes, user_data, handwriting),
            filter_classes_by_handwriting(classes, user_data, handwriting))


def get_most_common_priority(list):
    seen = []
    max_value = 0

    for x in list:
        count_x = sum(1 if x == y else 0 for y in list)
        if count_x > max_value:
            max_value = count_x
        if x not in [a[0] for a in seen]:
            seen.append((x, count_x))

    for x, count in seen:
        if max_value == count:
            return x


#todo riscrivi
def majority3_on_predictions(prediction1, prediction2, prediction3):
    mixed_pre = []
    for a, b, c in zip(prediction1, prediction2, prediction3):
        mixed_pre.append(get_most_common_priority([a, b, c]))
    return mixed_pre

def majority4_on_predictions(prediction1, prediction2, prediction3, prediction4):
    mixed_pre = []
    for a, b, c, d in zip(prediction1, prediction2, prediction3, prediction4):
        mixed_pre.append(get_most_common_priority([a, b, c, d]))
    return mixed_pre

def majority12_on_predictions(a0, b0, c0, d0, e0, f0, g0, h0, i0, l0, m0, n0):
    mixed_pre = []
    for a,b,c, d,e,f, g,h,i, l,m,n in zip(a0,b0,c0, d0,e0,f0, g0,h0,i0, l0,m0,n0):
        mixed_pre.append(get_most_common_priority([a,b,c, d,e,f, g,h,i, l,m,n]))
    return mixed_pre

# tuned_parameters = [{'kernel': ['rbf'], 'gamma': [1e-3, 1e-4, 1e-2, 1e-1, 1e-5], 'C': [0.1, 1, 10, 100, 500, 1000,  2500, 5000, 7500,10000]},
#                     {'kernel': ['linear'], 'C': [0.1, 1, 10, 100, 500, 1000, 2500, 5000, 7500,10000]}]
#                     #{'kernel': ['poly'], 'C': [1, 10, 100, 1000], 'degree':[2, 3, 4, 5, 6], 'gamma': [1e-3, 1e-4]}]
# scoring = ['precision_macro', 'recall_macro', 'f1_macro']

tuned_parameters = [{'kernel': ['rbf'], 'gamma': [1e-3, 1e-4, 1e-2, ], 'C': [10, 500, 1000, 2500, 5000, 7500]},
                    {'kernel': ['linear'], 'C': [100, 500, 1000, 2500, 5000]}]
# {'kernel': ['poly'], 'C': [1, 10, 100, 1000], 'degree':[2, 3, 4, 5, 6], 'gamma': [1e-3, 1e-4]}]
scoring = ['f1_macro']


class Learner:

    # @staticmethod
    # def binarize_classes(classes):
    #     lb = preprocessing.LabelBinarizer()
    #     y =lb.fit_transform(classes)
    #     return y, lb

    @staticmethod
    def scale_features(X_train, X_test):
        scaler = StandardScaler()
        scaler.fit(X_train)
        return scaler.transform(X_train), scaler.transform(X_test)

    def __init__(self, dataset_name):
        self.feature_manager = fm.FeaturesManager(dataset_name, update_data=True)
        self.features = self.feature_manager.get_features()
        self.classes = self.feature_manager.get_classes()
        self.classes_data = self.feature_manager.get_classes_data()

    def get_data_splitted(self, label, handwriting, random_state=None, test_size=0.3):
        x, y = filter_by_handwriting(self.features[label], self.classes, self.classes_data, handwriting)
        xtrain, xtest, y_train, y_test = train_test_split(x, y, random_state=random_state, test_size=test_size)
        X_train, X_test = Learner.scale_features(xtrain, xtest)

        return X_train, X_test, y_train, y_test

    # def train_ovs_svc(self, X_train, y_train):
    #     classifier = OneVsRestClassifier(SVC(C=1000, kernel="rbf"))
    #     classifier.fit(X_train, y_train)
    #     return classifier

    def train_gridsearch_svc(self, X_train, y_train):
        # classifier = GridSearchCV(SVC(probability=True), tuned_parameters, scoring=scoring, cv=5, refit='f1_macro', n_jobs=-1)
        classifier = SVC()
        classifier.fit(X_train, y_train)
        # print(classifier.best_params_)
        # print(classifier.best_score_)
        # print(classifier.best_estimator_)
        # print(classifier.scorer_)
        return classifier

    def print_report(self, handwriting, label, y_true, y_pred, target_names=None):
        print("Results for: {}  -  {}".format(handwriting.upper(), label))
        print()
        c = classification_report(y_true, y_pred, target_names=target_names)
        print(c)
        print()

    from pandas.util.testing import assert_series_equal
    def perform_simulation(self):
        hands = [Utils.ITALIC, Utils.BLOCK_LETTER]
        # {handwriting: {TIMED_SERIES_POINT: (x_train, x_test, predictions)}}
        predictions = {h: {l: None for l in Utils.TIMED_POINTS_SERIES_TYPE} for h in hands}
        # {handwriting: (y_train, y_test}
        hand_classes = {h: None for h in hands}

        for hand in [Utils.ITALIC, Utils.BLOCK_LETTER]:
            r = random.randint(0, 1000)
            print("################################### {} ###################################".format(hand))

            for label in Utils.TIMED_POINTS_SERIES_TYPE:
                X_train, X_test, y_train, y_test = self.get_data_splitted(label, hand, test_size=0.30, random_state=r)
                if hand_classes[hand] is not None:
                    assert_series_equal(hand_classes[hand], y_test)
                else:
                    hand_classes[hand] = y_test

                classifier = self.train_gridsearch_svc(X_train, y_train)
                y_pred = classifier.predict(X_test)
                predictions[hand][label] = y_pred

                self.print_report(hand, label, y_test, y_pred)

            a = majority3_on_predictions(predictions[hand][Utils.MOVEMENT_POINTS],
                                         predictions[hand][Utils.TOUCH_UP_POINTS],
                                         predictions[hand][Utils.TOUCH_DOWN_POINTS])
            self.print_report(hand, "MAJORITY ON NON SHIFTED POINTS (on movements, up, down)", hand_classes[hand], a)

            a = majority3_on_predictions(predictions[hand][Utils.X_SHIFTED_MOVEMENT_POINTS],
                                         predictions[hand][Utils.X_SHIFTED_TOUCH_UP_POINTS],
                                         predictions[hand][Utils.X_SHIFTED_TOUCH_DOWN_POINTS])
            self.print_report(hand, "MAJORITY ON X-SHIFTED POINTS (on movements, up, down)", hand_classes[hand], a)

            a = majority3_on_predictions(predictions[hand][Utils.Y_SHIFTED_MOVEMENT_POINTS],
                                         predictions[hand][Utils.Y_SHIFTED_TOUCH_UP_POINTS],
                                         predictions[hand][Utils.Y_SHIFTED_TOUCH_DOWN_POINTS])
            self.print_report(hand, "MAJORITY ON Y-SHIFTED POINTS (on movements, up, down)", hand_classes[hand], a)

            a = majority3_on_predictions(predictions[hand][Utils.XY_SHIFTED_MOVEMENT_POINTS],
                                         predictions[hand][Utils.XY_SHIFTED_TOUCH_UP_POINTS],
                                         predictions[hand][Utils.XY_SHIFTED_TOUCH_DOWN_POINTS])
            self.print_report(hand, "MAJORITY ON XY-SHIFTED POINTS (on movements, up, down)", hand_classes[hand], a)

            a = majority4_on_predictions(predictions[hand][Utils.MOVEMENT_POINTS],
                                         predictions[hand][Utils.X_SHIFTED_MOVEMENT_POINTS],
                                         predictions[hand][Utils.Y_SHIFTED_MOVEMENT_POINTS],
                                         predictions[hand][Utils.XY_SHIFTED_MOVEMENT_POINTS])
            self.print_report(hand, "MAJORITY ON ALL MOVEMENTS POINTS (considering non shifted and shifted)", hand_classes[hand], a)

            a = majority4_on_predictions(predictions[hand][Utils.TOUCH_UP_POINTS],
                                         predictions[hand][Utils.X_SHIFTED_TOUCH_UP_POINTS],
                                         predictions[hand][Utils.Y_SHIFTED_TOUCH_UP_POINTS],
                                         predictions[hand][Utils.XY_SHIFTED_TOUCH_UP_POINTS])
            self.print_report(hand, "MAJORITY ON ALL UP POINTS (considering non shifted and shifted)", hand_classes[hand], a)

            a = majority4_on_predictions(predictions[hand][Utils.TOUCH_DOWN_POINTS],
                                         predictions[hand][Utils.X_SHIFTED_TOUCH_DOWN_POINTS],
                                         predictions[hand][Utils.Y_SHIFTED_TOUCH_DOWN_POINTS],
                                         predictions[hand][Utils.XY_SHIFTED_TOUCH_DOWN_POINTS])
            self.print_report(hand, "MAJORITY ON ALL DOWN POINTS (considering non shifted and shifted)", hand_classes[hand], a)

            a = majority12_on_predictions(predictions[hand][Utils.MOVEMENT_POINTS],
                                          predictions[hand][Utils.X_SHIFTED_MOVEMENT_POINTS],
                                          predictions[hand][Utils.Y_SHIFTED_MOVEMENT_POINTS],
                                          predictions[hand][Utils.XY_SHIFTED_MOVEMENT_POINTS],

                                          predictions[hand][Utils.TOUCH_UP_POINTS],
                                          predictions[hand][Utils.X_SHIFTED_TOUCH_UP_POINTS],
                                          predictions[hand][Utils.Y_SHIFTED_TOUCH_UP_POINTS],
                                          predictions[hand][Utils.XY_SHIFTED_TOUCH_UP_POINTS],

                                          predictions[hand][Utils.TOUCH_DOWN_POINTS],
                                          predictions[hand][Utils.X_SHIFTED_TOUCH_DOWN_POINTS],
                                          predictions[hand][Utils.Y_SHIFTED_TOUCH_DOWN_POINTS],
                                          predictions[hand][Utils.XY_SHIFTED_TOUCH_DOWN_POINTS]
                                          )
            self.print_report(hand, "MAJORITY ON ALL",hand_classes[hand], a)


if __name__ == '__main__':
    l = Learner(Utils.DATASET_NAME_0)
    l.perform_simulation()
