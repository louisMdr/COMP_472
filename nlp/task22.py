from nlp import driver
from scraping.api import ImdbApi
from scraping.review_parser import ReviewParser
from pipeline.dataset import DataSet
from pipeline.bayes import NaiveBayesClassifier
import matplotlib.pyplot as plt


def run():
    delta_values = [1.0, 1.2, 1.4, 1.6, 1.8, 2.0]  # list of the different delta values we will be testing
    accuracy_values = []                           # list of the corresponding accuracy values for each delta value
    #parser = ReviewParser(show_id='tt4158110')  # same as driver.py -------------------------------------------------
    #parser.scrape()                                # essentially we are running driver.py with different delta values
    #parser.episodes.to_csv()                       # and extracting the accuracy for each
    #dataset = DataSet(parser.reviews)              # Actually I may not need lines 11-16 if I run main()
    #X, y = dataset.train_test_split()           # -------------------------------------------------------------------
    X, y = driver.task22_X, driver.task22_y
    for each in delta_values:                        # so now we run NB classifier multiple times,
        NaiveBayesClassifier.DEFAULT_DELTA = each    # using the different delta_values for DEFAULT_DELTA
        print('\n Using DELTA =', each)              # (print the delta we are working with)
        nbc = NaiveBayesClassifier(training_data=X)  # dr
        nbc.train()                                  # dr
        if each == 1.6:                                       # For when DELTA = 1.6 ...
            nbc.export_training_data('smooth-model.txt')  # We must export the training results to smooth-model.txt

                                      ## error - need to figure out how to save to smooth-model.txt

            preds = nbc.predict(y)                   # dr
            acc = nbc.validate(preds, y)        #### store the accuracy in variable acc (which we will later append)
                                                # (However for that we need func nbc.validate to return the accuracy)
            nbc.export_predictions(preds, y, 'smooth-result.txt')  # We must export predictions to smooth-results.txt

                                      ## error - need to figure out how to save to smooth-result.txt

            print('\nFiles smooth-model.txt & smooth-results.txt for DELTA = 1.6 saved. ')
        else:
            # nbc.export_training_data()        #### may not be necessary
            preds = nbc.predict(y)                   # dr
            acc = nbc.validate(preds, y)        #### store the accuracy in variable acc (which we will later append)
                                                # (However for that we need function validate to return the accuracy)
            # nbc.export_predictions(preds, y)  #### may not be necessary

        accuracy_values.append(acc)                  # append the accuracies to accuracy_values (list of accuracies)

    print('--------- Graph ---------')
    plt.plot(delta_values, accuracy_values)          # plotting the graph w values from delta_values & accuracy_values
    plt.xlabel('Delta values')
    plt.ylabel('Accuracy values')
    plt.show()
