from typing import List
import matplotlib.pyplot as plt

from nlp.scraping.data import Review
from nlp.pipeline.bayes import NaiveBayesClassifier


class FrequencyClassifier(NaiveBayesClassifier):

    ITER_MAP = {
        0: 0,
        1: 1,
        2: 10,
        3: 20,
        4: 5,
        5: 10,
        6: 20
    }

    iteration: int

    def __init__(self, threshold: float = None, training_data: List[Review] = None, delta: float = None):
        self.iteration = 0
        super().__init__(threshold, training_data, delta)


    def prepare(self, training_data: List[Review]):
        super().prepare(training_data)
        preprocessed = self.training_data.copy()
        preprocessed['count'] = 1
        preprocessed = preprocessed.groupby('word', as_index=False)['count'].sum().sort_values('count', ascending=False).reset_index(drop=True)
        if self.iteration > 3:
            preprocessed['cumsum'] = preprocessed['count'].cumsum()
            preprocessed['cumpct'] = (preprocessed['cumsum'] / self.training_data.shape[0]) * 100
            preprocessed = preprocessed[preprocessed['cumpct'] > self.ITER_MAP[self.iteration]]
        else:
            preprocessed = preprocessed[preprocessed['count'] > self.ITER_MAP[self.iteration]]
        self.training_data = self.training_data[self.training_data['word'].isin(preprocessed['word'].tolist())]
        self.iteration += 1


class FrequencyIterator:

    X: List[Review]
    y: List[Review]

    def __init__(self, X: List[Review], y: List[Review]):
        self.X = X
        self.y = y

    def iterate(self):
        results = []
        print('\nStarting Task 2.1 - Infrequent Word Filtering...\n')
        fc = FrequencyClassifier()
        for i in range(max(FrequencyClassifier.ITER_MAP.keys()) + 1):
            print(f'  Iteration {i + 1}')
            fc.train(training_data=self.X)
            fc.export_training_data(filename=f'frequency-model_{i + 1}.txt')
            preds = fc.predict(self.y)
            res = fc.calculate_accuracy(preds, self.y)
            fc.export_predictions(preds, self.y, filename=f'frequency-result_{i + 1}.txt')
            print(f'    Accuracy: {res}')
            results.append((i + 1, fc.training_data.shape[0], res))
        print('\nTask 2.1 complete. Graph: \n')
        plt.plot([i[0] for i in results], [i[2] for i in results])
        plt.title('Naives Bayes Classification with Frequency (2.1)')
        plt.ylabel('Accuracy')
        plt.xlabel('Iteration: Training Words')
        plt.xticks([i[0] for i in results], [f'{i[0]}: {i[1]}' for i in results])
        plt.show()
