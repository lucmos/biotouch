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


from sklearn.preprocessing import label_binarize

if __name__ == '__main__':
    f = fm.FeaturesManager()
    x = f.get_features()[MOVEMENT_POINTS]

    # print(f.get_features()[TOUCH_DOWN_POINTS].equals(f.get_features()[TOUCH_DOWN_POINTS]))
    # print(f.get_features()[TOUCH_DOWN_POINTS].equals(f.get_features()[TOUCH_UP_POINTS]))
    y = f.get_classes()

    # dividing X, y into train and test data
    X_train, X_test, y_train, y_test = train_test_split(x, y, random_state=0)

    # training a linear SVM classifier
    from sklearn.svm import SVC

    svm_model_linear = SVC(kernel='linear', C=1).fit(X_train, y_train)
    svm_predictions = svm_model_linear.predict(X_test)

    # model accuracy for X_test
    accuracy = svm_model_linear.score(X_test, y_test)

    # creating a confusion matrix
    cm = confusion_matrix(y_test, svm_predictions)

    # y = label_binarize(classes, classes)
    # n_classes = 3
    #
    # X_train, X_test, y_train, y_test = train_test_split(features, y, test_size = 0.25, random_state = 0)
    print(cm)

    # clf = svm.SVC(kernel='linear', C=1).fit(X_train, y_train)
    #
    # predictions = clf.predict(X_test)
    #
    # false_positive_rate, true_positive_rate, thresholds = roc_curve(actual, predictions)
    # roc_auc = auc(false_positive_rate, true_positive_rate)
    #
    # plt.title('Receiver Operating Characteristic')
    # plt.plot(false_positive_rate, true_positive_rate, 'b',
    #          label='AUC = %0.2f' % roc_auc)
    # plt.legend(loc='lower right')
    # plt.plot([0, 1], [0, 1], 'r--')
    # plt.xlim([-0.1, 1.2])
    # plt.ylim([-0.1, 1.2])
    # plt.ylabel('True Positive Rate')
    # plt.xlabel('False Positive Rate')
    # plt.show()
    # classifier



    # clf = OneVsRestClassifier(LinearSVC(random_state=0), n_jobs=4)
    # y_score = clf.fit(X_train, y_train).decision_function(X_test)
    #
    # # Compute ROC curve and ROC area for each class
    # fpr = dict()
    # tpr = dict()
    # roc_auc = dict()
    # for i in range(n_classes):
    #     fpr[i], tpr[i], _ = roc_curve(y_test[:, i], y_score[:, i])
    #     roc_auc[i] = auc(fpr[i], tpr[i])
    #
    # # Plot of a ROC curve for a specific class
    # for i in range(n_classes):
    #     plt.figure()
    #     plt.plot(fpr[i], tpr[i], label='ROC curve (area = %0.2f)' % roc_auc[i])
    #     plt.plot([0, 1], [0, 1], 'k--')
    #     plt.xlim([0.0, 1.0])
    #     plt.ylim([0.0, 1.05])
    #     plt.xlabel('False Positive Rate')
    #     plt.ylabel('True Positive Rate')
    #     plt.title('Receiver operating characteristic example')
    #     plt.legend(loc="lower right")
    #     plt.show()