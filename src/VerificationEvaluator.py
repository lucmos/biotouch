import sklearn.metrics
import time

import src.Learner as lr
import src.Utils as Utils
import src.Plotter as p

SVM_LIST = [lr.MOVEMENT, lr.UP, lr.DOWN, lr.MAJORITY, lr.AVERAGE, lr.WEIGHTED_AVERAGE,
            lr.XY_MOVEMENT, lr.XY_UP, lr.XY_DOWN, lr.XY_MAJORITY, lr.XY_AVERAGE, lr.XY_WEIGHTED_AVERAGE,
            lr.ALL_MAJORITY, lr.ALL_AVERAGE, lr.ALL_WEIGHTED_AVERAGE]


SVM_LIST_NOSHIFT = [lr.MOVEMENT, lr.UP, lr.DOWN, lr.MAJORITY, lr.AVERAGE, lr.WEIGHTED_AVERAGE]
SVM_LIST_SHIFT = [lr.XY_MOVEMENT, lr.XY_UP, lr.XY_DOWN, lr.XY_MAJORITY, lr.XY_AVERAGE, lr.XY_WEIGHTED_AVERAGE,]
SVM_LIST_COMP1 = [lr.MOVEMENT, lr.XY_MOVEMENT]
SVM_LIST_COMP2 = [lr.MOVEMENT, lr.ALL_MAJORITY, lr.ALL_AVERAGE, lr.ALL_WEIGHTED_AVERAGE]


class VerificationEvaluator:

    @staticmethod
    def compute_fnr(tpr):
        return [1 - x for x in tpr]

    @staticmethod
    def compute_tnr(fpr):
        return [1 - x for x in fpr]

    def compute_fpr_tpr_thresholds(self, svm_name, balanced):
        xtest, ytest, y = self.classifier.get_testdata_verification(balanced)
        true_classes, confidences = a.verification_proba(svm_name, xtest, ytest, y)
        fpr, tpr, thresholds = sklearn.metrics.roc_curve(true_classes, confidences, drop_intermediate=False)
        fpr = [0] + list(fpr) + [1]
        tpr = [0] + list(tpr) + [1]
        thresholds = [1] + list(thresholds) + [0]
        return fpr, tpr, thresholds

    def __init__(self, classifier):
        self.classifier = classifier

        svm_names = []
        fprs = []
        tprs = []
        aucs = []
        for svm_name in SVM_LIST_NOSHIFT:
            svm_names.append(svm_name)
            fpr, tpr, t = self.compute_fpr_tpr_thresholds(svm_name, True)
            fprs.append(fpr)
            tprs.append(tpr)
            aucs.append(sklearn.metrics.auc(fpr, tpr))
            p.Plotter(Utils.DATASET_NAME_0).plotFRRvsFPR(svm_name, t, self.compute_fnr(tpr), fpr, classifier.handwriting)

        p.Plotter(Utils.DATASET_NAME_0).plotRocs(svm_names, fprs, tprs, aucs, classifier.handwriting)








if __name__ == '__main__':
    a = lr.WordClassifier(Utils.DATASET_NAME_0, Utils.ITALIC)
    #

    import matplotlib.pyplot as plt
    plt.style.use('ggplot')
    VerificationEvaluator(a).compute_fpr_tpr_thresholds(lr.UP, True)

    import matplotlib as mpl

    # plt.style.use('fivethirtyeight')

    #
    # mpl.rcParams["figure.facecolor"] = 'white'
    # mpl.rcParams["axes.facecolor"] = 'white'
    # mpl.rcParams["axes.edgecolor"] = 'white'
    # mpl.rcParams["savefig.facecolor"] = 'white'
    from matplotlib import rcParams
