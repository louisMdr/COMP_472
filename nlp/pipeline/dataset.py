import html
import random
from typing import List, Optional, Tuple

from nlp.scraping.data import Review


class DataSet:

    DEFAULT_SPLIT = .5
    DEFAULT_THRESHOLD = 8.0

    raw_data: Optional[List[Review]]
    test_set: Optional[List[Review]]
    train_set: Optional[List[Review]]

    def __init__(self, data: List[Review] = None):
        self.raw_data = None
        self.train_set = None
        self.test_set = None
        if data is not None:
            self.__set(data)

    def __set(self, data: List[Review]):
        self.raw_data = data
        self.train_set = None
        self.test_set = None
        self.__clean()

    def __clean(self):
        for review in self.raw_data:
            review.contents = html.unescape(review.contents)
            review.contents = review.contents.lower()

    def set_raw_data(self, data: List[Review]):
        self.__set(data)

    def train_test_split(self,
                         split: float = None,
                         threshold: float = None,
                         data: List[Review] = None) -> Tuple[List[Review], List[Review]]:
        self.split(split, threshold, data)
        return self.train_set, self.test_set

    def split(self, split: float = None, threshold: float = None, data: List[Review] = None):
        def random_paritions(lst: List[Review], split_pct: float) -> Tuple[List[Review], List[Review]]:
            div = len(lst) * split_pct
            random.shuffle(lst)
            return lst[0: int(div)], lst[int(div)::]

        if split is None:
            split = self.DEFAULT_SPLIT

        if threshold is None:
            threshold = self.DEFAULT_THRESHOLD

        if data is not None:
            self.__set(data)

        # classify as positive or negative
        positive, negative = [], []
        for sample in self.raw_data:
            if sample.rating >= threshold:
                positive.append(sample)
            else:
                negative.append(sample)
        # partition
        positive_train, positive_test = random_paritions(positive, split)
        negative_train, negative_test = random_paritions(negative, split)
        # recombine
        self.train_set = positive_train + negative_train
        self.test_set = positive_test + negative_test

