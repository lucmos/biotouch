import logging
import random
from collections import OrderedDict, Counter
from datetime import datetime
from statistics import mean

import numpy as np
from sklearn.model_selection import GridSearchCV
from sklearn.svm import SVC

logging.basicConfig(level=logging.ERROR)

import sklearn
import sklearn.preprocessing
import sklearn.model_selection
import sklearn.metrics
import sklearn.calibration
import operator
import pandas
import warnings
import json
import src.Chronometer as Chronom

warnings.filterwarnings("ignore", category=sklearn.exceptions.UndefinedMetricWarning)

import src.Utils as Utils
import src.FeatureManager as fm

LEARNING_FROM = Utils.TIMED_POINTS_SERIES_TYPE

MOVEMENT = Utils.MOVEMENT_POINTS
UP = Utils.TOUCH_UP_POINTS
DOWN = Utils.TOUCH_DOWN_POINTS
MAJORITY = "majority"
AVERAGE = "average"
WEIGHTED_AVERAGE = "weighted_average"

XY_MOVEMENT = Utils.XY_SHIFTED_MOVEMENT_POINTS
XY_UP = Utils.XY_SHIFTED_TOUCH_UP_POINTS
XY_DOWN = Utils.XY_SHIFTED_TOUCH_DOWN_POINTS
XY_MAJORITY = "xy_majority"
XY_AVERAGE = "xy_average"
XY_WEIGHTED_AVERAGE = "xy_weighted_average"

ALL_MAJORITY = "all_majority"
ALL_AVERAGE = "all_average"
ALL_WEIGHTED_AVERAGE = "all_weighted_average"

SVM_LIST = [MOVEMENT, UP, DOWN, MAJORITY, AVERAGE, WEIGHTED_AVERAGE,
            XY_MOVEMENT, XY_UP, XY_DOWN, XY_MAJORITY, XY_AVERAGE, XY_WEIGHTED_AVERAGE,
            ALL_MAJORITY, ALL_AVERAGE, ALL_WEIGHTED_AVERAGE]

MOVEMENT_WEIGHT = 0.75


# SVM TUNING
TUNED_PARAMETERS = [{'kernel': ['rbf'], 'gamma': [0, 1e-1, 1e-2, 1e-3, 1e-4, 1e-5, 1e-6],
                     'C': [0.1, 1, 10, 100, 500, 1000, 2500, 5000, 7500, 10000]}]
CV = 5

class WordClassifier:

    @staticmethod
    def most_common(lst):
        c = Counter(lst)
        return max(lst, key=c.get)

    @staticmethod
    def majority_vote(list_of_list):
        return [WordClassifier.most_common(x) for x in zip(*list_of_list)]

    @staticmethod
    def index_at_max_value(probs):
        index, value = max(enumerate(probs), key=operator.itemgetter(1))
        return index

    def majority_vote_proba(self, list_of_probs, majority_predicted):
        # todo ====> The probabilities are actually estimated, majority_vote_proba and majority_vote may yeld different results

        # # get each svm which class has chosen
        # list_of_chosen = [[WordClassifier.index_at_max_value(x) for x in probs] for probs in list_of_probs]
        # # get for each instance which one is the class with the majority vote
        # list_of_chosen_majority = WordClassifier.majority_vote(list_of_chosen)

        # Majority_predicted are used in order to reduce the impact of the estimation of the probabilities.
        # convert the classes to integer
        majority_predicted_int = [list(self.get_classes_()).index(x) for x in majority_predicted]

        # return the classification performed by the svm that did the best on the majority value
        return [max(x, key=lambda o: o[majority_position]) for majority_position, x in
                zip(majority_predicted_int, zip(*list_of_probs))]

    def max_proba_class(self, list_of_probs):
        return [list(self.get_classes_())[WordClassifier.index_at_max_value(x)] for x in list_of_probs]

    @staticmethod
    def average_proba(list_of_probs):
        return [[mean(y) for y in zip(*x)] for x in zip(*list_of_probs)]

    def weighted_average_proba(self, list_of_probs):
        probs = []
        for x in zip(*list_of_probs):
            other_weights = (1 - self.mov_weight) / (len(x) - 1)
            mov_weighted = [[a * self.mov_weight for a in v] for v in x[0:1]]
            others_weighted = [[a * other_weights for a in v] for v in x[1:]]
            probabilities = [mean(y) for y in zip(*(mov_weighted + others_weighted))]
            z = sum(probabilities)
            probs.append([v / z for v in probabilities])
        return probs

    @staticmethod
    def filter_by_handwriting(dataframe, classes, user_data, handwriting):
        d_temp = dataframe.join(classes).join(user_data[Utils.HANDWRITING], on=Utils.USER_ID).drop(Utils.USER_ID,
                                                                                                   axis=1)
        dataframe_filt = d_temp[d_temp[Utils.HANDWRITING] == handwriting].drop(Utils.HANDWRITING, axis=1)

        c_temp = pandas.DataFrame(classes).join(user_data[Utils.HANDWRITING], on=Utils.USER_ID)
        classes_filt = c_temp[c_temp[Utils.HANDWRITING] == handwriting].drop(Utils.HANDWRITING, axis=1).squeeze()

        return dataframe_filt, classes_filt

    @staticmethod
    def scale_features(x_train, x_test):
        scaler = sklearn.preprocessing.StandardScaler()
        scaler.fit(x_train)
        return scaler.transform(x_train), scaler.transform(x_test)

    def split_scale_data(self, label, handwriting, test_size, stratify=True, random_state=None):
        x, y = WordClassifier.filter_by_handwriting(self.features[label], self.classes, self.classes_data, handwriting)
        xtrain, xtest, y_train, y_test = sklearn.model_selection.train_test_split(x, y,
                                                                                  stratify=y if stratify else None,
                                                                                  random_state=random_state,
                                                                                  test_size=test_size)
        X_train, X_test = WordClassifier.scale_features(xtrain, xtest)
        return X_train, X_test, y_train, y_test

    def __init__(self, dataset_name, handwriting, test_size=0.3125, update_data=False, check_consistency=False, weight=MOVEMENT_WEIGHT):
        self.dataset_name = dataset_name
        self.handwriting = handwriting

        self.feature_manager = fm.FeaturesManager(dataset_name, update_data)
        self.features = self.feature_manager.get_features()
        self.classes = self.feature_manager.get_classes()
        self.classes_data = self.feature_manager.get_classes_data()

        self.X_train = {x: None for x in LEARNING_FROM}
        self.X_test = {x: None for x in LEARNING_FROM}
        self.y_train = None
        self.y_test = None

        self.check_inconsistency = check_consistency

        random.seed(datetime.now())
        r = random.randint(0, 10000)
        for label in LEARNING_FROM:
            a, b, c, d = self.split_scale_data(label, handwriting, test_size, random_state=r)
            self.X_train[label], self.X_test[label] = a, b

            if self.y_train is not None or self.y_test is not None:
                assert (self.y_train == c).all()
                assert (self.y_test == d).all()
            else:
                self.y_train = c
                self.y_test = d

        self.svms = {}
        self.mov_weight = weight

        self.predict_functions = {
            MOVEMENT: lambda svms, xtest: svms[MOVEMENT].predict(xtest[MOVEMENT]),
            UP: lambda svms, xtest: svms[UP].predict(xtest[UP]),
            DOWN: lambda svms, xtest: svms[DOWN].predict(xtest[DOWN]),
            MAJORITY: lambda svms, xtest: WordClassifier.majority_vote(
                (svms[x].predict(xtest[x]) for x in [MOVEMENT, UP, DOWN])),
            AVERAGE: lambda svms, xtest: self.max_proba_class(self.predict_proba_functions[AVERAGE](svms, xtest)),
            WEIGHTED_AVERAGE: lambda svms, xtest: self.max_proba_class(
                self.predict_proba_functions[WEIGHTED_AVERAGE](svms, xtest)),

            XY_MOVEMENT: lambda svms, xtest: svms[XY_MOVEMENT].predict(xtest[XY_MOVEMENT]),
            XY_UP: lambda svms, xtest: svms[XY_UP].predict(xtest[XY_UP]),
            XY_DOWN: lambda svms, xtest: svms[XY_DOWN].predict(xtest[XY_DOWN]),
            XY_MAJORITY: lambda svms, xtest: WordClassifier.majority_vote(
                (svms[x].predict(xtest[x]) for x in [XY_MOVEMENT, XY_UP, XY_DOWN])),
            XY_AVERAGE: lambda svms, xtest: self.max_proba_class(self.predict_proba_functions[XY_AVERAGE](svms, xtest)),
            XY_WEIGHTED_AVERAGE: lambda svms, xtest: self.max_proba_class(
                self.predict_proba_functions[XY_WEIGHTED_AVERAGE](svms, xtest)),

            ALL_MAJORITY: lambda svms, xtest: WordClassifier.majority_vote(
                (svms[x].predict(xtest[x]) for x in [MOVEMENT, XY_MOVEMENT, UP, XY_UP, DOWN, XY_DOWN])),
            ALL_AVERAGE: lambda svms, xtest: self.max_proba_class(
                self.predict_proba_functions[ALL_AVERAGE](svms, xtest)),
            ALL_WEIGHTED_AVERAGE: lambda svms, xtest: self.max_proba_class(
                self.predict_proba_functions[ALL_WEIGHTED_AVERAGE](svms, xtest)),
        }

        self.predict_proba_functions = {
            MOVEMENT: lambda svms, xtest: svms[MOVEMENT].predict_proba(xtest[MOVEMENT]),
            UP: lambda svms, xtest: svms[UP].predict_proba(xtest[UP]),
            DOWN: lambda svms, xtest: svms[DOWN].predict_proba(xtest[DOWN]),
            MAJORITY: lambda svms, xtest: self.majority_vote_proba(
                [svms[x].predict_proba(xtest[x]) for x in [MOVEMENT, UP, DOWN]],
                self.predict_functions[MAJORITY](svms, xtest)),
            AVERAGE: lambda svms, xtest: WordClassifier.average_proba(
                [svms[x].predict_proba(xtest[x]) for x in [MOVEMENT, UP, DOWN]]),
            WEIGHTED_AVERAGE: lambda svms, xtest: self.weighted_average_proba(
                [svms[x].predict_proba(xtest[x]) for x in [MOVEMENT, UP, DOWN]]),

            XY_MOVEMENT: lambda svms, xtest: svms[XY_MOVEMENT].predict_proba(xtest[XY_MOVEMENT]),
            XY_UP: lambda svms, xtest: svms[XY_UP].predict_proba(xtest[XY_UP]),
            XY_DOWN: lambda svms, xtest: svms[XY_DOWN].predict_proba(xtest[XY_DOWN]),
            XY_MAJORITY: lambda svms, xtest: self.majority_vote_proba(
                (svms[x].predict_proba(xtest[x]) for x in [XY_MOVEMENT, XY_UP, XY_DOWN]),
                self.predict_functions[XY_MAJORITY](svms, xtest)),
            XY_AVERAGE: lambda svms, xtest: WordClassifier.average_proba(
                (svms[x].predict_proba(xtest[x]) for x in [XY_MOVEMENT, XY_UP, XY_DOWN])),
            XY_WEIGHTED_AVERAGE: lambda svms, xtest: self.weighted_average_proba(
                [svms[x].predict_proba(xtest[x]) for x in [XY_MOVEMENT, XY_UP, XY_DOWN]]),

            ALL_MAJORITY: lambda svms, xtest: self.majority_vote_proba(
                (svms[x].predict_proba(xtest[x]) for x in [MOVEMENT, XY_MOVEMENT, UP, XY_UP, DOWN, XY_DOWN]),
                self.predict_functions[ALL_MAJORITY](svms, xtest)),
            ALL_AVERAGE: lambda svms, xtest: WordClassifier.average_proba(
                (svms[x].predict_proba(xtest[x]) for x in [MOVEMENT, XY_MOVEMENT, UP, XY_UP, DOWN, XY_DOWN])),
            ALL_WEIGHTED_AVERAGE: lambda svms, xtest: self.weighted_average_proba(
                [svms[x].predict_proba(xtest[x]) for x in [MOVEMENT, XY_MOVEMENT, UP, XY_UP, DOWN, XY_DOWN]])
        }
        self.fit()


    def _initialize_svm(self):
        self.svms = {}
        for label in LEARNING_FROM:
            # self.svms[label] = sklearn.calibration.CalibratedClassifierCV(SVC(), cv=8) #todo implementa grid search
            # self.svms[label] = SVC(probability=True)  # todo implementa grid search
            self.svms[label] = GridSearchCV(SVC(probability=True), TUNED_PARAMETERS, cv=CV, n_jobs=-1)

            # todo esplora approcci ovo e ovr

    def fit(self):
        self._initialize_svm()
        chrono = Chronom.Chrono("Fitting svms...")
        for label in LEARNING_FROM:
            self.svms[label].fit(self.X_train[label], self.y_train)

        # todo: check consistenza ordinamento, forse si può togliere
        for l1 in LEARNING_FROM:
            for l2 in LEARNING_FROM:
                assert (self.svms[l1].classes_ == self.svms[l2].classes_).all()
        chrono.end()
        if self.check_inconsistency:
            self.check_inconsistencies()

    def predict(self, svm_name, x_test, mov_weight):
        assert svm_name in self.predict_functions, "Predict function not valid"
        self.mov_weight = mov_weight
        fun = self.predict_functions[svm_name]
        return fun(self.svms, x_test)

    def predict_proba(self, svm_name, x_test, mov_weight):
        assert svm_name in self.predict_proba_functions, "Predict proba function not valid"
        self.mov_weight = mov_weight
        fun = self.predict_proba_functions[svm_name]
        return fun(self.svms, x_test)

    def verification_proba(self, svm_name, x_test, y_verify, y_true, mov_weight):
        assert svm_name in self.predict_proba_functions, "Predict proba function not valid {}".format(svm_name)
        assert len(y_verify) == len(y_true), "There must be an y to verify for each instance {} != {}".format(len(x_test), len(y_verify))
        assert not(svm_name in LEARNING_FROM) or len(x_test[svm_name]) == len(y_verify)
        self.mov_weight = mov_weight
        true_classes = []
        confidences = []
        for x, y, t in zip(self.predict_proba(svm_name, x_test, mov_weight), y_verify, y_true):
            true_classes.append(y == t)
            confidences.append(x[self.class_to_index(y)])
        return true_classes, confidences

    def verification(self, svm_name, x_test, y_verify, y_true, treshold, mov_weight):
        assert svm_name in self.predict_proba_functions, "Predict proba function not valid"
        assert len(x_test[svm_name]) == len(y_verify), "There must be an y to verify for each instance {} != {}".format(
            len(x_test), len(y_verify))
        self.mov_weight = mov_weight
        return ([a == b for a, b in zip(y_verify, y_true)],
                [x[self.class_to_index(y)] >= treshold for x, y in zip(self.predict_proba(svm_name, x_test, mov_weight), y_verify)])

    def get_traindata(self):
        return self.X_train, self.y_train

    def get_testdata(self):
        return self.X_test, self.y_test

    def get_data_recap(self):
        return json.dumps(OrderedDict((x, OrderedDict(
            (("X_train", len(self.X_train[x])),
             ("y_train", len(self.y_train)),
             ("X_test", len(self.X_test[x])),
             ("y_test", len(self.y_test)),)
        )) for x in LEARNING_FROM), indent=4)

    def __str__(self):
        return self.get_data_recap()

    def get_classes_(self):
        return list(self.svms[MOVEMENT].classes_)

    def index_to_class(self, index):
        assert 0 <= index < len(self.get_classes_()), "Wrong index"
        return self.get_classes_()[index]

    def prob_to_class(self, probabilities):
        return self.index_to_class(WordClassifier.index_at_max_value(probabilities))

    def class_to_index(self, string_class):
        return self.get_classes_().index(string_class)

    def prob_to_index(self, probabilities):
        return WordClassifier.index_at_max_value(probabilities)

    def check_inconsistencies(self):
        chrono = Chronom.Chrono("Checking consistency...")
        counter = 0
        inc = []
        # print(self.get_classes_())
        for svm in SVM_LIST:
            predicted = self.predict(svm, self.get_testdata()[0])
            predicted_proba = self.predict_proba(svm, self.get_testdata()[0])
            for i, (a, b) in enumerate(zip(predicted, predicted_proba)):
                if a != self.prob_to_class(b):
                    counter += 1
                    inc.append(({"predicted": a}, {self.index_to_class(i): a for i, a in enumerate(b)},
                                {"class with max proba": self.prob_to_class(b)},
                                {"correct one": list(self.get_testdata()[1])[i]}))
                    # print(a,b,self.prob_to_class((b)))
        chrono.end("found {} inconsistencies".format(counter))
        return inc

    def get_testdata_verification(self, balanced):
        all_classes = self.get_classes_()
        ver_xtest = {x: [] for x in LEARNING_FROM}
        ver_ytest = []
        ver_ytrue = []
        for iy, y in enumerate(self.get_testdata()[1]):
            if not balanced:
                for y_test in all_classes:
                    ver_ytrue.append(y)
                    ver_ytest.append(y_test)
                    for series in LEARNING_FROM:
                        ver_xtest[series].append(self.get_testdata()[0][series][iy])
            else:
                for to_add in (y, random.choice(list(filter(lambda x: x != y, all_classes)))):
                    ver_ytrue.append(y)
                    ver_ytest.append(to_add)
                    for series in LEARNING_FROM:
                        ver_xtest[series].append(self.get_testdata()[0][series][iy])

        return ver_xtest, ver_ytest, ver_ytrue


if __name__ == '__main__':
    a = WordClassifier(Utils.DATASET_NAME_0, Utils.ITALIC)
    a.fit()
    print(a)
    print()
    print("Inconsistencies")
    for b in a.check_inconsistencies():
        print(json.dumps(b, indent=4))
