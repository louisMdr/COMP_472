import re
import html
import random
import string
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
        translator = str.maketrans('', '', string.punctuation)
        emoji_pattern = re.compile(
            "["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map symbols
            u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
            u"\U00002500-\U00002BEF"  # chinese char
            u"\U00002702-\U000027B0"
            u"\U00002702-\U000027B0"
            u"\U000024C2-\U0001F251"
            u"\U0001f926-\U0001f937"
            u"\U00010000-\U0010ffff"
            u"\u2640-\u2642" 
            u"\u2600-\u2B55"
            u"\u200d"
            u"\u23cf"
            u"\u23e9"
            u"\u231a"
            u"\ufe0f"  # dingbats
            u"\u3030"
            "]+", re.UNICODE
        )

        for review in self.raw_data:
            review.contents = html.unescape(review.contents)
            review.contents = re.sub(emoji_pattern, '', review.contents.lower().translate(translator))

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

