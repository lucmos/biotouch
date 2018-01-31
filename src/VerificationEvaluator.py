import src.Learner as lr
from src import Utils


class VerificationEvaluator:

    def __init__(self, classifier):
        self.classifier = classifier


if __name__ == '__main__':

    classsifier = lr.WordClassifier(Utils.DATASET_NAME_0, Utils.ITALIC)
    classsifier.fit()
