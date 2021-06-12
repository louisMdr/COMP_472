from bs4.element import Tag
from typing import Optional, List

from nlp.scraping.api import ImdbApi
from nlp.scraping.data import Episode, Review, EpisodeList


class ReviewParser:

    api: ImdbApi
    show_id: Optional[str]
    show_name: Optional[str]
    reviews: List[Review]
    episodes: EpisodeList

    def __init__(self, show_id: str = None, show_name: str = None):
        if show_id is None and show_name is None:
            raise RuntimeError('At least one of show_id, show_name must be set')

        self.show_id = show_id
        self.show_name = show_name
        self.api = ImdbApi()
        self.reviews = []
        self.episodes = EpisodeList()

    def scrape(self):
        show_soup = self.api.get_title_as_bs4(self.show_id)
        if self.show_name is None:
            self.show_name = show_soup.find_all('h1', attrs={'data-testid': 'hero-title-block__title'})[0].text
        print(f'Scraping data for show: {self.show_name}')
        episode_info = show_soup.find_all('div', attrs={'data-testid': 'episodes-header'})[0]
        num_eps_span = episode_info.find_all('span', attrs={'class': 'ipc-title__subtext'})[0]
        num_episodes = int(num_eps_span.text)
        seasons_info = show_soup.find_all('label', attrs={'for': 'browse-episodes-season'})[0]
        # seasons_info = show_soup.find_all('label', attrs={'class': 'ipc-simple-select__label'})
        num_seasons = int(seasons_info.text.split(' ')[0])
        seasons_info: Tag = show_soup.find_all('select', attrs={'id': 'browse-episodes-season'})[0]
        season_nums = [
            int(child.text) for child in seasons_info.children
            if child.name == 'option' and 'value' in child.attrs.keys() and child.text.isnumeric()
        ]
        print(f'   Found {num_seasons} seasons')
        self.__scrape_seasons(num_seasons, season_nums)
        print(f'   Scraped {len(self.episodes)} episodes, {len(self.reviews)} reviews')

    def __scrape_seasons(self, num_seasons: int, season_nums: list):
        for season_num in sorted(season_nums):
            print(f'   Scraping season: {season_num}')
            season_soup = self.api.get_episodes_for_season_as_bs4(self.show_id, season_num)
            episode_list = season_soup.find_all('div', attrs={'class': 'list detail eplist'})[0]
            for ep_item in episode_list.children:
                if not isinstance(ep_item, Tag):
                    continue
                # extract information about the season episodes in the seasons
                ep_num = int(ep_item.find('meta', attrs={'itemprop': 'episodeNumber'}).attrs['content'])
                air_date = ep_item.find('div', attrs={'class': 'airdate'}).text.strip()
                episode_info = ep_item.find('div', attrs={'class': 'info'}).find('strong').find('a')
                episode_name = episode_info.text.strip()
                episode_id = episode_info.attrs['href'].split('/')[2]
                self.episodes.add(Episode(
                    episode_num=ep_num,
                    season_num=season_num,
                    episode_id=episode_id,
                    episode_name=episode_name,
                    air_date=air_date
                ))
                # extract reviews for the episodes
                episode_reviews = self.api.get_episode_reviews_as_bs4(episode_id)
                self.episodes.get(-1).review_url = self.api.current_page
                reviews = episode_reviews.find('div', attrs={'class': 'lister-list'})
                ep_rev_counter = 0
                for review in reviews.children:
                    if not isinstance(review, Tag):
                        continue
                    rating = review.find('svg', attrs={'class': 'ipl-icon'})
                    if rating is None:
                        continue
                    review_rating = float(rating.find_next('span').text)
                    review_content = review.find('div', attrs={'class': 'content'}).find('div', attrs={'class': 'text show-more__control'}).text
                    self.reviews.append(Review(episode_id, review_rating, review_content))
                    ep_rev_counter += 1
                print(f'      Scraped episode {ep_num}: \'{episode_name}\' with {ep_rev_counter} reviews')
