import pandas
import src.FeatureManager as fm
import src.Utils as Utils
from src.Constants import *
from src.Chronometer import Chrono
from sklearn import svm
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_curve, auc
import matplotlib.pyplot as plt
import random
from sklearn.metrics import roc_curve, auc
from sklearn import datasets
from sklearn.multiclass import OneVsRestClassifier
from sklearn.svm import LinearSVC
from sklearn.metrics import confusion_matrix
from sklearn.preprocessing import MinMaxScaler

from sklearn.metrics import classification_report
from sklearn.svm import SVC
from collections import Counter
from sklearn.preprocessing import *
# form sklearn.model_selection import GridSearchCV

import numpy as np
from matplotlib import pyplot as plt

from sklearn.datasets import make_hastie_10_2
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import make_scorer
from sklearn.metrics import accuracy_score
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import label_binarize
from sklearn.metrics import precision_score

def filter_dataframe_by_handwriting(dataframe, classes, user_data, handwriting):
    temp = dataframe.join(classes).join(user_data[HANDWRITING], on=USER_ID).drop(USER_ID, axis=1)
    return temp[temp[HANDWRITING] == handwriting].drop(HANDWRITING, axis=1)


def filter_classes_by_handwriting(classes, user_data, handwriting):
    temp = pandas.DataFrame(classes).join(user_data[HANDWRITING], on=USER_ID)
    return temp[temp[HANDWRITING] == handwriting].drop(HANDWRITING, axis=1).squeeze()


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


def brute_testing1():
    f = fm.FeaturesManager(DATASET_NAME_0)

    for h in [ITALIC, BLOCK_LETTER]:

        print("...............................", h, "...................................")
        y = f.get_classes()
        user_data = f.get_classes_data()

        predictions = {}
        X_train = {}
        y_train = {}
        X_test = {}
        y_test = {}
        a = None
        r = random.randint(0, 100000)
        for label in TIMED_POINTS_SERIES_TYPE:
            x = f.get_features()[label]
            x, y = filter_by_handwriting(x, y, user_data, h)

            X_train[label], X_test[label], y_train[label], y_test[label] = train_test_split(x, y, random_state=r,
                                                                                            test_size=0.3)
            scaler = StandardScaler()
            x = scaler.fit(X_train[label])
            X_train[label] = scaler.transform(X_train[label])
            X_test[label] = scaler.transform(X_test[label])
            if a is not None:
                assert a.equals(y_train[label])
                a = y_train[label]

        for label in TIMED_POINTS_SERIES_TYPE:
            print("Testing on: " + label)
            svm_model_linear = SVC(kernel='linear', C=1).fit(X_train[label], y_train[label])
            svm_predictions = svm_model_linear.predict(X_test[label])
            predictions[label] = svm_predictions
            print(classification_report(y_test[label], svm_predictions))
            # print(confusion_matrix(y_test[label], svm_predictions))

        mixed_pre = []
        print("Testing on: majority results")
        for a, b, c in zip(predictions[MOVEMENT_POINTS], predictions[TOUCH_UP_POINTS], predictions[TOUCH_DOWN_POINTS]):
            mixed_pre.append(get_most_common_priority([a, b, c]))
        print(classification_report(y_test[MOVEMENT_POINTS], mixed_pre))


from sklearn.model_selection import GridSearchCV, cross_val_score
import numpy as np

if __name__ == '__main__':
    f = fm.FeaturesManager(DATASET_NAME_0)

    for h in [ITALIC, BLOCK_LETTER]:

        print("...............................", h, "...................................")
        y = f.get_classes()
        user_data = f.get_classes_data()

        predictions = {}
        X_train = {}
        y_train = {}
        X_test = {}
        y_test = {}
        a = None
        r = random.randint(0, 100000)

        # Set the parameters by cross-validation
        tuned_parameters = [{'kernel': ['rbf'], 'gamma': [1e-3, 1e-4],
                             'C': [1, 10, 100, 1000]},
                            {'kernel': ['linear'], 'C': [1, 10, 100, 1000]},
                            {'kernel': ['poly'], 'C': [1, 10, 100, 1000], 'degree':[2, 3, 4, 5, 6], 'gamma': [1e-3, 1e-4]}]
        scoring = {'AUC': 'roc_auc', 'Accuracy': make_scorer(accuracy_score), 'Precision': make_scorer(precision_score)}

        for label in TIMED_POINTS_SERIES_TYPE:
            x = f.get_features()[label]
            x, y = filter_by_handwriting(x, y, user_data, h)

            X_train[label], X_test[label], y_train[label], y_test[label] = train_test_split(x, y, random_state=r,
                                                                                            test_size=0.3)
            scaler = StandardScaler()
            x = scaler.fit(X_train[label])
            X_train[label] = scaler.transform(X_train[label])
            X_test[label] = scaler.transform(X_test[label])

        for label in TIMED_POINTS_SERIES_TYPE:
            print("Testing on: " + label)
            classifier = GridSearchCV(SVC(), tuned_parameters, cv=5, refit='AUC', n_jobs=-1)
            classifier = classifier.fit(X_train[label], y_train[label])
            predictions[label] = classifier.predict(X_test[label])
            print("Best parameters set found on development set:")
            print()
            print(classifier.best_params_)
            print(classifier.best_score_)
            print(classifier.best_estimator_)
            # print("Grid scores on development set:")
            # print()
            # means = classifier.cv_results_['mean_test_score']
            # stds = classifier.cv_results_['std_test_score']
            # for mean, std, params in zip(means, stds, classifier.cv_results_['params']):
            #     print("%0.3f (+/-%0.03f) for %r"
            #           % (mean, std * 2, params))
            print()

            print("Detailed classification report:")
            print()
            print("The model is trained on the full development set.")
            print("The scores are computed on the full evaluation set.")
            print()
            y_true, y_pred = y_test[label], classifier.predict(X_test[label])
            print(classification_report(y_true, y_pred))
            print()


        mixed_pre = []
        print("Testing on: majority results")
        for a, b, c in zip(predictions[MOVEMENT_POINTS], predictions[TOUCH_UP_POINTS], predictions[TOUCH_DOWN_POINTS]):
            mixed_pre.append(get_most_common_priority([a, b, c]))
        print(classification_report(y_test[MOVEMENT_POINTS], mixed_pre))
