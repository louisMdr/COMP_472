from nlp.scraping.api import ImdbApi
from nlp.scraping.review_parser import ReviewParser
from nlp.pipeline.dataset import DataSet


def main():
    parser = ReviewParser(show_id='tt4158110')
    parser.scrape()
    # print('\n\n\nCSV OUTPUT::\n\n')
    print(parser.episodes.to_csv())
    dataset = DataSet(parser.reviews)
    X, y = dataset.train_test_split()
    print('finished')


if __name__ == '__main__':
    main()