#import bob
import matplotlib.pyplot as plt
import src.Plotter as pl
import src.Learner as lrn
import numpy as np
import sklearn.metrics

from src import Utils

plt.style.use('fivethirtyeight')
# plt.style.use('ggplot')

import matplotlib as mpl
#
# class IdentificationEvaluator:
#     def __init__(self, cms_probabilities , y_test, class_list):
#         self.cms_values=[]
#         self.cms_probabilities=cms_probabilities
#         self.y_test=y_test
#         self.class_list=class_list
#         assert len(y_test)==len(cms_probabilities)
#
#
#     def fill_cms_values(self):
#         self.cms_values=[]
#         for i in range(0, len(self.class_list)):
#             cms_val_i = 0
#             for prob_list, y in zip(self.cms_probabilities, self.y_test):
#                 y_prob = prob_list[list(self.class_list).index(y)]
#                 if sum(1 for a in prob_list if a > y_prob) <= i:
#                     cms_val_i += 1
#
#             self.cms_values.append(cms_val_i / float(len(self.y_test)))
#         print(self.cms_values)
#         return self.cms_values

class IdentificationEvaluator:
    def __init__(self, classifier : lrn.WordClassifier):
        self.classifier = classifier

    def cms_curve(self, svm_name):
        x_test, y_test = self.classifier.get_testdata()
        classes = self.classifier.get_classes_()
        y_estimated = self.classifier.predict_proba(svm_name, x_test) #todo, gestisci peso weighted avg

        cms_values = []
        for i in range(0, len(classes)):
            cms_val_i = 0
            for probs, y in zip(y_estimated, y_test):
                y_prob = probs[self.classifier.class_to_index(y)]
                if sum(1 for a in probs if a > y_prob) <= i:
                    cms_val_i += 1

            cms_values.append(cms_val_i / float(len(y_test)))
        return list(range(0, len(classes)+1)), [0] + cms_values

if __name__ == '__main__':
    a = lrn.WordClassifier(Utils.DATASET_NAME_0, Utils.ITALIC)
    SVM_LIST_NOSHIFT = [lrn.MOVEMENT, lrn.UP, lrn.DOWN, lrn.MAJORITY, lrn.AVERAGE, lrn.WEIGHTED_AVERAGE]
    c = IdentificationEvaluator(a)
    r = []
    v = []
    n = []
    for s in SVM_LIST_NOSHIFT:
        rank, values = c.cms_curve(s)
        n.append(s)
        r.append(rank)
        v.append(values)
        pl.Plotter(Utils.DATASET_NAME_0).plotCMC(s, rank, values, a.handwriting)

    pl.Plotter(Utils.DATASET_NAME_0).plotCMCs(n, r, v, a.handwriting)
#     learner=lrn.WordClassifier(Utils.DATASET_NAME_0, Utils.ITALIC)
#     learner.fit()
#     x, y=learner.get_testdata()
#     classesList=learner.get_classes_()
#     probs=learner.predict_proba(lrn.MOVEMENT, x)
#
#     classes_indexes=[]
#     for a,b in enumerate(classesList):
#         classes_indexes.append(a+1)
# #######################################################################################################################
#     learner2 = lrn.WordClassifier(Utils.DATASET_NAME_0, Utils.ITALIC)
#     learner2.fit()
#     x2, y2 = learner2.get_testdata()
#     classesList2 = learner2.get_classes_()
#     probs2 = learner2.predict_proba(lrn.MOVEMENT, x2)
#
#     classes_indexes2 = []
#     for a, b in enumerate(classesList2):
#         classes_indexes2.append(a + 1)
# ########################################################################################################################
#     learner3 = lrn.WordClassifier(Utils.DATASET_NAME_0, Utils.BLOCK_LETTER)
#     learner3.fit()
#     x3, y3 = learner3.get_testdata()
#     classesList3 = learner3.get_classes_()
#     probs3 = learner3.predict_proba(lrn.MOVEMENT, x3)
#
#     classes_indexes3 = []
#     for a, b in enumerate(classesList3):
#         classes_indexes3.append(a + 1)
#
#
#     '''l = IdentificationEvaluator([[ 0.96697155  ,0.03302845],[ 0.00746219  ,0.99253781],[ 0.00951699  ,0.99048301],[ 0.95638103  ,0.04361897],
#                                  [ 0.8036171   ,0.1963829 ],[ 0.8036171   ,0.1963829 ],[ 0.8036171   ,0.1963829 ],[ 0.01786314  ,0.98213686],
#                                  [ 0.96559608  ,0.03440392],[ 0.96077084  ,0.03922916],[ 0.01264261  ,0.98735739],[ 0.81518927  ,0.18481073],
#                                  [ 0.01102044  ,0.98897956],[ 0.95441381  ,0.04558619],[ 0.94432064  ,0.05567936],[ 0.00675033  ,0.99324967],
#                                  [ 0.00960538  ,0.99039462],[ 0.96840267  ,0.03159733],[ 0.95344436  ,0.04655564],[ 0.02739944  ,0.97260056]],
#
#                                 ["adriano_ischiboni_was-lx1a_0_ITALIC","alessandro_spini_was-lx1a_0_ITALIC","alessandro_spini_was-lx1a_0_ITALIC",
#                                 "adriano_ischiboni_was-lx1a_0_ITALIC","alessandro_spini_was-lx1a_0_ITALIC","adriano_ischiboni_was-lx1a_0_ITALIC",
#                                 "alessandro_spini_was-lx1a_0_ITALIC","alessandro_spini_was-lx1a_0_ITALIC","adriano_ischiboni_was-lx1a_0_ITALIC",
#                                 "adriano_ischiboni_was-lx1a_0_ITALIC","alessandro_spini_was-lx1a_0_ITALIC","adriano_ischiboni_was-lx1a_0_ITALIC",
#                                 "alessandro_spini_was-lx1a_0_ITALIC","adriano_ischiboni_was-lx1a_0_ITALIC","adriano_ischiboni_was-lx1a_0_ITALIC",
#                                 "alessandro_spini_was-lx1a_0_ITALIC","alessandro_spini_was-lx1a_0_ITALIC","adriano_ischiboni_was-lx1a_0_ITALIC",
#                                 "adriano_ischiboni_was-lx1a_0_ITALIC","alessandro_spini_was-lx1a_0_ITALIC"],
#
#                                 ["adriano_ischiboni_was-lx1a_0_ITALIC","alessandro_spini_was-lx1a_0_ITALIC"])'''
#     l1=IdentificationEvaluator(probs, y, classesList)
#     l2=IdentificationEvaluator(probs2, y2, classesList2)
#     l3=IdentificationEvaluator(probs3, y3, classesList3)
#     #l1.fill_cms_values()
#     #luca=sklearn.metrics.classification_report(y,[learner.prob_to_class(j) for j in probs])
#     #print(luca)
#
#     #p= pl.Plotter(Utils.DATASET_NAME_0).simplePlot(classes_indexes,l1.fill_cms_values())
#     p1=pl.Plotter(Utils.DATASET_NAME_0).simplePlot_multiple([[classes_indexes,l1.fill_cms_values(), "CMC italic1"],[classes_indexes,l2.fill_cms_values(),"CMC italic2"],[classes_indexes,l3.fill_cms_values(),"CMC block letters1"]])