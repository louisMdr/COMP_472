from nlp import task22
from nlp.scraping.api import ImdbApi
from nlp.scraping.review_parser import ReviewParser
from nlp.pipeline.dataset import DataSet
from nlp.pipeline.bayes import NaiveBayesClassifier

task22_X = None
task22_y = None

def main():
    # Keeping Up With The Kardashians   tt1086761
    # Westworld   tt0475784
    # Mr Robot tt4158110
    # Game of Thrones tt0944947
    # The Sopranos tt0141842
    parser = ReviewParser(show_id='tt4158110')
    parser.scrape()
    # print('\n\n\nCSV OUTPUT::\n\n')
    parser.episodes.to_csv()
    dataset = DataSet(parser.reviews)
    X, y = dataset.train_test_split()
    task22_X = X
    task22_y = y
    nbc = NaiveBayesClassifier(training_data=X)
    nbc.train()
    nbc.export_training_data()
    preds = nbc.predict(y)
    nbc.validate(preds, y)
    nbc.export_predictions(preds, y)


if __name__ == '__main__':
    print('Running Task 1:\n\n')
    main()

    print('\n\nRunning Task 2:\n\n')
    user_input = ''
    while user_input != '##':
        user_input = input('Which task would you like to run?\nEnter 2.1, 2.2, 2.3, or ## to exit: ')
        if user_input == '2.1':
         #   task21.run()
            print('\nrunning 2.1\n')
        elif user_input == '2.2':
            task22.run()
            print('\n\n')
        elif user_input == '2.3':
         #   task23.run()
            print('\nrunning 2.3\n')
        elif user_input == '##':
            break
        else:
           print('\nTry again.')
    print('\nProgram will now terminate.')
