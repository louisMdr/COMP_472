import os
import re
import math
import numpy as np
import pandas as pd
from typing import Optional, List

from nlp.scraping.data import Review


class NaiveBayesClassifier:

    DEFAULT_SPLIT = .5
    DEFAULT_THRESHOLD = 8.0
    DEFAULT_DELTA = 1.0

    training_data: Optional[pd.DataFrame]
    probabilities: Optional[pd.DataFrame]
    positive_document_prob: Optional[float]
    negative_document_prob: Optional[float]
    threshold: float
    delta: float
    stopwords: List[str]
    count_positive_words: Optional[int]
    count_negative_words: Optional[int]
    vocab_length: Optional[int]

    def __init__(self, threshold: float = None, training_data: List[Review] = None, delta: float = None):
        self.threshold = threshold
        self.delta = delta
        self.training_data = None
        self.probabilities = None
        self.negative_document_prob = None
        self.positive_document_prob = None
        self.count_positive_words = None
        self.count_negative_words = None
        self.vocab_length = None
        self.__load_stopwords()
        if training_data is not None:
            self.prepare(training_data)

    def __load_stopwords(self):
        dirname = os.path.dirname(__file__)
        with open(os.path.join(dirname, 'stopwords.txt'), 'r') as f:   ### replace stopwords.txt with remove.txt
            self.stopwords = f.read().split('\n')

    def __prepare(self, data: List[Review], with_rating: bool = False) -> List[dict]:
        for_pandas = []
        for review in data:
            # add all words in review
            for_pandas.extend([
                {
                    **{
                        'word': word,
                        'length': len(word),
                        'review_id': review.review_id
                    },
                    **({'review_rating': review.rating} if with_rating else {})
                }
                for word in re.split(r'\s+', review.contents)
                # if not with_rating -> in prediction mode, so always include words
                # if word not in self.stopwords -> in training mode, so only include non-stopwords
                if word != '' and (not with_rating or word not in self.stopwords)
            ])
        return for_pandas

    def prepare(self, training_data: List[Review]):
        self.training_data = pd.DataFrame(self.__prepare(training_data, with_rating=True))
        # self.training_data.to_csv('prepared_data.csv', index=False)

    def train(self, training_data: List[Review] = None, threshold: float = None, delta: float = None):
        if threshold is not None:
            self.threshold = threshold
        if self.threshold is None:
            self.threshold = NaiveBayesClassifier.DEFAULT_THRESHOLD
        if delta is not None:
            self.delta = delta
        if self.delta is None:
            self.delta = NaiveBayesClassifier.DEFAULT_DELTA
        if training_data is not None:
            self.prepare(training_data)
        if self.training_data is None:
            raise RuntimeError('There is no data to train on!')
        # prepare
        self.training_data['count'] = 1
        self.training_data['negative'] = np.where(self.training_data['review_rating'] < self.threshold, 1, 0)
        self.training_data['positive'] = np.where(self.training_data['review_rating'] >= self.threshold, 1, 0)
        # calculate denominators
        self.count_positive_words = len(self.training_data[self.training_data.positive == 1]['word'])
        self.count_negative_words = len(self.training_data[self.training_data.negative == 1]['word'])
        num_positive_revs = len(self.training_data[self.training_data.positive == 1]['review_id'].unique())
        num_negative_revs = len(self.training_data[self.training_data.negative == 1]['review_id'].unique())
        # perform grouping to get counts in each category and merge back together
        self.probabilities = pd.merge(
            # group on word and calculate counts for positive category
            self.training_data[self.training_data.positive == 1].groupby('word', as_index=False)['count'].sum().rename(columns={'count': 'positive_count'}),
            # group on word and calculate counts for negative category
            self.training_data[self.training_data.negative == 1].groupby('word', as_index=False)['count'].sum().rename(columns={'count': 'negative_count'}),
            on='word',
            how='outer'
        ).fillna(0)
        self.vocab_length = len(self.probabilities['word'].unique())
        # calculate conditional probabilities for words
        # add smoothing with delta
        self.probabilities['cond_positive'] = (self.probabilities['positive_count'] + self.delta) / (self.count_positive_words + (self.delta * self.vocab_length))
        self.probabilities['cond_negative'] = (self.probabilities['negative_count'] + self.delta) / (self.count_negative_words + (self.delta * self.vocab_length))

        # calculate document probabilities
        self.positive_document_prob = num_positive_revs / (num_negative_revs + num_positive_revs)
        self.negative_document_prob = num_negative_revs / (num_negative_revs + num_positive_revs)

    def predict(self, data: List[Review]) -> dict:
        def single_predict(series: pd.Series, cond_key: str, count: int) -> float:
            # check if the word is in the trained words
            if series['word'] in self.probabilities['word'].to_list():
                value = math.log(
                    self.probabilities.loc[self.probabilities['word'] == series['word'], cond_key].values[0] *
                    series['count']
                )
            else:
                # return the log of the probability of an untrained word
                value = math.log((self.delta * series['count']) / (count + (self.delta * self.vocab_length)))
            return value

        def inner_predict(df: pd.DataFrame, doc_prob: float, cond_key: str, count: int) -> float:
            return (
                # probability of the document type
                math.log(doc_prob) +
                # calculate and sum probabilities of all words in the document
                df.apply(lambda x: single_predict(x, cond_key, count), axis=1).sum()
            )

        def predict_pos(df: pd.DataFrame) -> float:
            return inner_predict(df, self.positive_document_prob, 'cond_positive', self.count_positive_words)

        def predict_neg(df: pd.DataFrame) -> float:
            return inner_predict(df, self.negative_document_prob, 'cond_negative', self.count_negative_words)

        to_predict = pd.DataFrame(self.__prepare(data))
        to_predict['count'] = 1
        grouped = to_predict.groupby(['review_id', 'word'], as_index=False)['count'].sum()
        grouped.to_csv('to_test.csv')
        # target_columns = ['review_id', 'positive_prob', 'negative_prob']
        # grouped = grouped.groupby('review_id').apply(lambda gdf: gdf.assign(
        #     positive_prob=predict_pos,
        #     negative_prob=predict_neg
        # ))[target_columns].groupby(target_columns, as_index=False)[target_columns]
        predictions = grouped.groupby('review_id').apply(lambda gdf: dict(
            positive_prob=predict_pos(gdf),
            negative_prob=predict_neg(gdf)
        ))
        return {
            name: {
                **pred,
                **{'prediction': 'positive' if pred['positive_prob'] >= pred['negative_prob'] else 'negative'}
            }
            for name, pred in predictions.iteritems()
        }

    def export_training_data(self, path_to_file: str = None, filename: str = 'model.txt'):
        if path_to_file is not None:
            filename = os.path.join(path_to_file, filename)
        exported_data = []
        for i, row in self.probabilities.sort_values(['positive_count', 'negative_count'], ascending=False).reset_index(drop=True).iterrows():
            exported_data.extend([
                f'No.{i + 1} {row["word"]}',
                f'{int(row["positive_count"])},{row["cond_positive"]},{int(row["negative_count"])},{row["cond_negative"]}'
            ])
        with open(filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(exported_data).encode('utf-8').decode('utf-8'))

    def validate(self, preds: dict, data: List[Review]):
        accuracy = self.calculate_accuracy(preds, data)
        print(f'Accuracy: {accuracy}')

    def calculate_accuracy(self, preds: dict, data: List[Review]) -> float:
        if not all([rev.review_id in preds.keys() for rev in data]):
            print('Missing some predictions... :(')

        return len([
            True for review in data
            if (
                (preds[review.review_id]['prediction'] == 'positive' and review.rating >= self.threshold) or
                (preds[review.review_id]['prediction'] == 'negative' and review.rating < self.threshold)
            )
        ]) / len(data)

    def export_predictions(self, preds: dict, data: List[Review], path_to_file: str = None, filename: str = 'result.txt'):
        if path_to_file is not None:
            filename = os.path.join(path_to_file, filename)
        exported_data = []
        for i, row in enumerate(data):
            pred = preds[row.review_id]
            true_val = 'negative' if row.rating < self.threshold else 'positive'
            res = 'right' if true_val == pred['prediction'] else 'wrong'
            exported_data.extend([
                f'No.{i + 1} {row.review_id}',
                f'{pred["positive_prob"]},{pred["negative_prob"]},{pred["prediction"]},{true_val},{res}'
            ])
        with open(filename, 'w', encoding='utf-8') as f:
            f.write('\n'.join(exported_data))


