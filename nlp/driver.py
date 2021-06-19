import random
from nlp.scraping.api import ImdbApi
from nlp.scraping.review_parser import ReviewParser
from nlp.pipeline.dataset import DataSet
from nlp.pipeline.bayes import NaiveBayesClassifier
from nlp.pipeline.frequency import FrequencyIterator


def main():
    # Keeping Up With The Kardashians   tt1086761
    # Westworld   tt0475784
    # Mr Robot tt4158110
    # Game of Thrones tt0944947
    # The Sopranos tt0141842
    # Modern Family tt1442437
    # H F-O tt1600194
    # Grey's Anatomy   tt0413573
    # Supernatural  tt0460681
    parser = ReviewParser(show_id='tt4158110')
    parser.scrape()
    # print('\n\n\nCSV OUTPUT::\n\n')
    parser.episodes.to_csv()
    dataset = DataSet(parser.reviews)
    X, y = dataset.train_test_split()
    frq = FrequencyIterator(X, y)
    frq.iterate()

    print('finished')


if __name__ == '__main__':
    main()
