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

from sklearn.metrics import classification_report
from sklearn.svm import SVC
from collections import Counter

# form sklearn.model_selection import GridSearchCV


from sklearn.preprocessing import label_binarize


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


if __name__ == '__main__':
    f = fm.FeaturesManager(DATASET_NAME_0)
    #    x = f.get_features()[MOVEMENT_POINTS]

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
        for label in TIMED_POINTS_SERIES_TYPE:
            x = f.get_features()[label]
            x, y = filter_by_handwriting(x, y, user_data, h)
            X_train[label], X_test[label], y_train[label], y_test[label] = train_test_split(x, y, random_state=2, test_size=0.3)
            if a is not None:
                assert a.equals(y_train[label])
                a = y_train[label]

        for label in TIMED_POINTS_SERIES_TYPE:

            print("Testing on: " + label)
            svm_model_linear = SVC(kernel='linear', C=1).fit(X_train[label], y_train[label])
            svm_predictions = svm_model_linear.predict(X_test[label])
            predictions[label] = svm_predictions
            print(classification_report(y_test[label], svm_predictions))

        mixed_pre = []
        print("Testing on: majority results")
        for a, b, c in zip(predictions[MOVEMENT_POINTS], predictions[TOUCH_UP_POINTS], predictions[TOUCH_DOWN_POINTS]):
            mixed_pre.append(get_most_common_priority( [a, b, c]))
        print(classification_report(y_test[MOVEMENT_POINTS], mixed_pre))

