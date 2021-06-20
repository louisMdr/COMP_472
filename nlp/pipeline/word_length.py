from typing import List
import matplotlib.pyplot as plt

from nlp.scraping.data import Review
from nlp.pipeline.bayes import NaiveBayesClassifier


class WordLengthClassifier(NaiveBayesClassifier):
    # the word with the following length to be removed from training data
    word_length_cap = [0, 2, 4, 9]

    # keeps track of which length of words to remove in each model preparation
    iteration: int

    def __init__(self, threshold: float = None, training_data: List[Review] = None, delta: float = None):
        # first number: 2
        self.iteration = 0
        # generate normal naive Classifier
        super().__init__(threshold, training_data, delta)

    # override the parent method of prepare
    def prepare(self, training_data: List[Review]):
        super().prepare(training_data)
        # copy list of X (list of reviews in the normal training data)
        new_training = self.training_data.copy()

        # checks if we are getting words = 0, (> 2 or 4) or words < 9 (last iteration)
        if self.iteration == 0:
          self.training_data = new_training
        elif self.iteration == 3:
            #since the assumption is gradual = cumulative, length must also be > 4 (= between 5 and 8 inclusive)
            new_training = new_training[new_training['length'] > self.word_length_cap[self.iteration-1]]
            new_training = new_training[new_training['length'] < self.word_length_cap[self.iteration]]
        else:
            new_training = new_training[new_training['length'] > self.word_length_cap[self.iteration]]
        # set new training data as the subset containing the filtered out words
        self.training_data = self.training_data[self.training_data['word'].isin(new_training['word'].tolist())]
        # next length
        self.iteration += 1


class WordLengthIterator:
    X: List[Review]
    y: List[Review]

    def __init__(self, X: List[Review], y: List[Review]):
        self.X = X
        self.y = y

    def iterate(self):
        #accuracy results
        accuracy_results = []
        #stores the word counts remaining in each iteration
        word_count_results = []
        print('\nStarting Task 2.3 - Word Length Filtering...\n')
        wlc = WordLengthClassifier()
        for element in WordLengthClassifier.word_length_cap:
            # print correct brackets
            if element == 0:
                print(f'  LENGTH = {element}')
            elif element == 9:
                print(f'  LENGTH <= {element}')
            else:
                print(f'  LENGTH >= {element}')
            # runs the above prepare function (generates training set)
            wlc.train(training_data=self.X)
            # report model data
            wlc.export_training_data(filename=f'length-model_{element}.txt')
            # test the model
            preds = wlc.predict(self.y)
            # calculate accuracy based on new training data
            res = wlc.calculate_accuracy(preds, self.y)
            # report results from test set Y
            wlc.export_predictions(preds, self.y, filename=f'length-result_{element}.txt')
            print(f'    Accuracy: {res}')
            # add new accuracy to list
            accuracy_results.append(res)
            #get vocab words count remaining
            word_count_results.append(wlc.training_data.shape[0])
        print('\nTask 2.3 complete. Graph: \n')
        #the amount of words removed
        keys = ["=0", "<=2", "<=4", ">=9"]
        # performance (accuracy here) against nbr words left ( = word lengths removed)
        plt.plot([f'{keys[i]}: {word_count_results[i]}' for i in len(word_count_results)], [i for i in accuracy_results])
        plt.title('Naives Bayes Classification with Word Length (2.3)')
        plt.ylabel('Accuracy')
        plt.xlabel('Words Left In Vocab')
        plt.show()
