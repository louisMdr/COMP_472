from nlp.scraping.api import ImdbApi
from nlp.scraping.review_parser import ReviewParser


def main():
    parser = ReviewParser(show_id='tt4158110')
    parser.scrape()
    # print('\n\n\nCSV OUTPUT::\n\n')
    print(parser.episodes.to_csv())


if __name__ == '__main__':
    main()