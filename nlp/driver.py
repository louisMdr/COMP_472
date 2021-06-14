from nlp.scraping.api import ImdbApi
from nlp.scraping.review_parser import ReviewParser
from nlp.pipeline.dataset import DataSet
from nlp.pipeline.bayes import NaiveBayesClassifier


def main():
    parser = ReviewParser(show_id='tt4158110')
    parser.scrape()
    # print('\n\n\nCSV OUTPUT::\n\n')
    parser.episodes.to_csv()
    dataset = DataSet(parser.reviews)
    X, y = dataset.train_test_split()
    nbc = NaiveBayesClassifier(training_data=X)
    nbc.train()
    nbc.export_training_data()
    preds = nbc.predict(y)
    nbc.validate(preds, y)
    nbc.export_predictions(preds, y)
    print('finished')


if __name__ == '__main__':
    main()
