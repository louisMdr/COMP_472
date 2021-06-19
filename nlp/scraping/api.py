import random
import requests
from typing import Optional
from bs4 import BeautifulSoup


class ImdbApi:

    _base: str
    _bs4_parser: str
    current_page: Optional[str]
    current_response: Optional[requests.Response]

    def __init__(self, bs4_parser: str = 'html.parser'):
        self._base = 'https://www.imdb.com/'
        self.current_page = None
        self.current_response = None
        self._bs4_parser = bs4_parser

    def request(self, method: str, url_parts: list, params: dict = None, payload: dict = None) -> requests.Response:
        # format params
        param_str = ''
        if params is not None:
            param_str = '?' + '&'.join([
                f'{k}={v}' if not isinstance(v, list) else '&'.join(f'{k}[]={v}')
                for k, v in params.items()
            ])
        self.current_page = f'{self._base}{"/".join(url_parts)}{param_str}'
        headers = {'Connection': 'close', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36'}
        self.current_response = requests.request(method, self.current_page, headers=headers)
        return self.current_response

    def get_title(self, title_id: str) -> requests.Response:
        return self.request('get', ['title', title_id])

    def get_title_as_bs4(self, title_id: str) -> BeautifulSoup:
        return BeautifulSoup(self.get_title(title_id).text, self._bs4_parser)

    def get_episodes(self, title_id: str) -> requests.Response:
        return self.request('get', ['title', title_id, 'episodes'])

    def get_episodes_as_bs4(self, title_id: str) -> BeautifulSoup:
        return BeautifulSoup(self.get_episodes(title_id).text, self._bs4_parser)

    def get_episodes_for_season(self, title_id: str, season_num: int) -> requests.Response:
        return self.request('get', ['title', title_id, 'episodes'], params={'season': str(season_num)})

    def get_episodes_for_season_as_bs4(self, title_id: str, season_num: int) -> BeautifulSoup:
        return BeautifulSoup(self.get_episodes_for_season(title_id, season_num).text, self._bs4_parser)

    def get_episode_reviews(self, episode_id: str) -> requests.Response:
        return self.request('get', ['title', episode_id, 'reviews'])

    def get_episode_reviews_as_bs4(self, episode_id: str) -> BeautifulSoup:
        return BeautifulSoup(self.get_episode_reviews(episode_id).text, self._bs4_parser)




