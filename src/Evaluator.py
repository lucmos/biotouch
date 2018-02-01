import sklearn.metrics

import src.Learner as lr
import src.Utils as Utils

import numpy as np

import src.Plotter as plotter
import src.Chronometer as cr

MOVEMENT_WEIGHT = lr.MOVEMENT_WEIGHT

def generate_svm_name(svm_name,  w=MOVEMENT_WEIGHT):
    name = svm_name
    if svm_name in [lr.WEIGHTED_AVERAGE, lr.XY_WEIGHTED_AVERAGE, lr.ALL_WEIGHTED_AVERAGE]:
        name += str(w)
    return name

class VerificationEvaluator:
    def __init__(self, classifier):
        self.classifier = classifier

    @staticmethod
    def compute_fnr(tpr):
        return [1 - x for x in tpr]

    @staticmethod
    def compute_tnr(fpr):
        return [1 - x for x in fpr]

    def compute_fpr_tpr_thresholds(self, svm_name, balanced, mov_weight=MOVEMENT_WEIGHT):
        xtest, ytest, y = self.classifier.get_testdata_verification(balanced)
        true_classes, confidences = self.classifier.verification_proba(svm_name, xtest, ytest, y, mov_weight)
        fpr, tpr, thresholds = sklearn.metrics.roc_curve(true_classes, confidences, drop_intermediate=False)
        fpr = [0] + list(fpr) + [1]
        tpr = [0] + list(tpr) + [1]
        thresholds = [1] + list(thresholds) + [0]
        return fpr, tpr, thresholds

    def plot_info(self, svm_name, b, w=MOVEMENT_WEIGHT):
        fpr, tpr, t = self.compute_fpr_tpr_thresholds(svm_name, b,  w)
        return generate_svm_name(svm_name, w), fpr, tpr, t, sklearn.metrics.auc(fpr, tpr)

    def plots_info_names(self, names, b, w=MOVEMENT_WEIGHT):
        svm_names = []
        fprs = []
        tprs = []
        ts = []
        aucs = []
        for svm_name in names:
            svm_names.append(generate_svm_name(svm_name, w))
            fpr, tpr, t = self.compute_fpr_tpr_thresholds(svm_name, b, w)
            ts.append(t)
            fprs.append(fpr)
            tprs.append(tpr)
            aucs.append(sklearn.metrics.auc(fpr, tpr))
        return names, fprs, tprs, ts, aucs

    def plots_info_weights(self, name, b, ws):
        names = []
        fprs = []
        tprs = []
        ts = []
        aucs = []
        for w in ws:
            names.append(generate_svm_name(name, w))
            fpr, tpr, t = self.compute_fpr_tpr_thresholds(name, b, w)
            ts.append(t)
            fprs.append(fpr)
            tprs.append(tpr)
            aucs.append(sklearn.metrics.auc(fpr, tpr))
        return names, fprs, tprs, ts, aucs


class IdentificationEvaluator:
    def __init__(self, classifier : lr.WordClassifier):
        self.classifier = classifier

    def cms_curve(self, svm_name, mov_weight=MOVEMENT_WEIGHT):
        x_test, y_test = self.classifier.get_testdata()
        classes = self.classifier.get_classes_()
        y_estimated = self.classifier.predict_proba(svm_name, x_test, mov_weight)

        cms_values = []
        for i in range(0, len(classes)):
            cms_val_i = 0
            for probs, y in zip(y_estimated, y_test):
                y_prob = probs[self.classifier.class_to_index(y)]
                if sum(1 for a in probs if a > y_prob) <= i:
                    cms_val_i += 1

            cms_values.append(cms_val_i / float(len(y_test)))
        return list(range(0, len(classes)+1)), [0] + cms_values

    def plot_info(self, name, w=MOVEMENT_WEIGHT):
        rank, value = self.cms_curve(name, w)
        return generate_svm_name(name, w),rank,value

    def plots_info_names(self, names, w=MOVEMENT_WEIGHT):
        svm_names = []
        ranks = []
        values = []
        for s in names:
            svm_names.append(generate_svm_name(s, w))
            rank, value = self.cms_curve(s, w)
            ranks.append(rank)
            values.append(value)
        return svm_names, ranks, values

    def plots_info_weights(self, name, ws):
        svm_names = []
        ranks = []
        values = []
        for w in ws:
            svm_names.append(generate_svm_name(name, w))
            rank, value =  self.cms_curve(name, w)
            ranks.append(rank)
            values.append(value)
        return svm_names, ranks, values


SVM_LIST = lr.SVM_LIST

SVM_LIST_NOSHIFT = [lr.MOVEMENT, lr.UP, lr.DOWN, lr.MAJORITY, lr.AVERAGE, lr.WEIGHTED_AVERAGE]
SVM_LIST_SHIFT = [lr.XY_MOVEMENT, lr.XY_UP, lr.XY_DOWN, lr.XY_MAJORITY, lr.XY_AVERAGE, lr.XY_WEIGHTED_AVERAGE,]

SVM_LIST_COMP1 = [lr.MOVEMENT, lr.XY_MOVEMENT]
SVM_LIST_COMP2 = [lr.MOVEMENT, lr.ALL_MAJORITY, lr.ALL_AVERAGE, lr.ALL_WEIGHTED_AVERAGE]

TO_DO_TOGHETER = [SVM_LIST_NOSHIFT, SVM_LIST_SHIFT, SVM_LIST_COMP1, SVM_LIST_COMP2]

# todo: ottimizza evitando la ripetizione di calcoli
if __name__ == '__main__':
    p = plotter.Plotter(Utils.DATASET_NAME_0)

    for handwriting in [Utils.ITALIC, Utils.BLOCK_LETTER]:
        classifier = lr.WordClassifier(Utils.DATASET_NAME_0, handwriting)

        chrono = cr.Chrono("Generating verification outputs...")
        ver = VerificationEvaluator(classifier)
        for balanced in [True, False]:
            names, fprs, tprs, ts, aucs = ver.plots_info_weights(lr.WEIGHTED_AVERAGE, balanced, np.arange(0, 1.01, 0.2))
            p.plotRocs(names, fprs, tprs, aucs, handwriting, balanced)

            for svm_list in TO_DO_TOGHETER:
                names, fprs, tprs, ts, aucs = ver.plots_info_names(svm_list, balanced)
                p.plotRocs(names, fprs, tprs, aucs, handwriting, balanced)

            for svm in SVM_LIST:
                name, fpr, tpr, t, auc = ver.plot_info(svm, balanced)
                p.plotRoc(name, fpr, tpr, auc, handwriting, balanced)
                p.plotFRRvsFPR(name, t, ver.compute_fnr(tpr), fpr, handwriting, balanced)
        chrono.end()

        chrono = cr.Chrono("Generating identification outputs...")
        ide = IdentificationEvaluator(classifier)
        svm_names, ranks, values = ide.plots_info_weights(lr.WEIGHTED_AVERAGE, np.arange(0, 1.01, 0.2))
        p.plotCMCs(svm_names, ranks, values, handwriting)

        for svm_list in TO_DO_TOGHETER:
            svm_names, ranks, values = ide.plots_info_names(svm_list)
            p.plotCMCs(svm_names, ranks, values, handwriting)

        for svm in SVM_LIST:
            svm_name, rank, value = ide.plot_info(svm)
            p.plotCMC(svm_name, rank, value, handwriting)
        chrono.end()
