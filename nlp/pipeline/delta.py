from typing import List
import matplotlib.pyplot as plt

from nlp.scraping.data import Review
from nlp.pipeline.bayes import NaiveBayesClassifier


class DeltaClassifier(NaiveBayesClassifier):
    # list of the different delta values we will be testing
    delta_values = [1.0, 1.2, 1.4, 1.6, 1.8, 2.0]
    # iteration variable (iter 0, 1, 2...)
    iteration: int

    def __init__(self, threshold: float = None, training_data: List[Review] = None, delta: float = None):
        # first iteration will be for delta = 1.0
        self.iteration = 0
        # generate a Naive Classifier
        super().__init__(threshold, training_data, delta)

    # override the parent method of prepare
    def prepare(self, training_data: List[Review]):
        super().prepare(training_data)
        self.iteration += 1


class DeltaIterator:
    X: List[Review]
    y: List[Review]

    # 2 attributes; training set and testing set
    def __init__(self, X: List[Review], y: List[Review]):
        self.X = X
        self.y = y

    # method that will iterate through the delta values,
    # train the data (ie: calculate the probabilities of the training set) based on the corresponding delta &
    # make the predictions on the testing set (for each iteration) based on those probabilities
    def iterate(self):
        # list of where the corresponding accuracy values of each delta will be stored
        accuracy_values = []
        print('\nStarting Task 2.2 - Word Smoothing Filtering...\n')
        # start a NB classifier
        dc = DeltaClassifier()
        # for every delta (1.0, 1.2, 1.4, ... 2.0)
        for element in DeltaClassifier.delta_values:
            print(f'  DELTA = {element}')
            # train the data (calculate the probabilities) using this delta
            dc.train(training_data=self.X, delta=element)
            # if delta = 1.6, we store our model and predictions in two new files (smooth-... .txt)
            if element == 1.6:
                dc.export_training_data(filename='smooth-model.txt')
                # make predictions on the testing set, based on the training set probabilities
                preds = dc.predict(self.y)
                # calculate the accuracy of the predictions
                acc = dc.calculate_accuracy(preds, self.y)
                print('    Accuracy:', acc)
                dc.export_predictions(preds, self.y, filename=f'smooth-result.txt')
                print('    Saving files "smooth-model.txt" & "smooth-result.txt" for delta = 1.6')
            else:
                # make predictions on the testing set, based on the training set probabilities
                preds = dc.predict(self.y)
                # calculate the accuracy of the predictions
                acc = dc.calculate_accuracy(preds, self.y)
                print('    Accuracy:', acc)
            # append the new found accuracy to the list of accuracy_values
            accuracy_values.append(acc)

        print('\nTask 2.2 complete. Graph: \n')
        # plotting the graph w values from delta_values & accuracy_values
        plt.plot(DeltaClassifier.delta_values, accuracy_values)
        plt.title('Naives Bayes Classification with Delta (2.2)')
        plt.ylabel('Accuracy')
        plt.xlabel('Delta')
        plt.show()
