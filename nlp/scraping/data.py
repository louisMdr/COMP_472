import os
from dateutil import parser
from typing import Optional, List


class Episode:
    """ Data container for episode """
    episode_num: int
    season_num: int
    episode_id: str
    review_url: Optional[str]
    episode_name: str
    air_date: str
    year: int

    def __init__(self, episode_num: int, season_num: int, episode_id: str, episode_name: str, air_date: str):
        self.episode_num = episode_num
        self.season_num = season_num
        self.episode_id = episode_id
        self.name = episode_name
        self.air_date = air_date
        try:
            self.year = parser.parse(air_date).year.real
        except Exception as e:
            self.year = -1
        self.review_url = None


class EpisodeList:
    """ Data container for multiple episodes """
    CSV_COLUMNS = [
        {'name': 'Name'},
        {'season_num': 'Season'},
        {'review_url': 'Review Link'},
        {'year': "Year"}
    ]

    episodes: List[Episode]

    def __init__(self):
        self.episodes = []

    def add(self, episode: Episode):
        self.episodes.append(episode)

    def get(self, idx: int) -> Episode:
        return self.episodes[idx]

    def as_csv(self) -> str:
        columns_str = ','.join([list(item.values())[0] for item in self.CSV_COLUMNS])
        if len(self.episodes) == 0:
            return columns_str
        values_str = '\n'.join([
            ','.join([
                str(episode.__dict__[list(item.keys())[0]])
                for item in self.CSV_COLUMNS
            ])
            for episode in self.episodes

        ])
        return f'{columns_str}\n{values_str}'

    def to_csv(self, path_to_file: str = None):
        if path_to_file is not None:
            filename = os.path.join(path_to_file, 'data.csv')
        else:
            filename = 'data.csv'
        with open(filename, 'w') as csv:
            csv.write(self.as_csv())

    def __len__(self) -> int:
        return len(self.episodes)


class Review:
    """ Data container for reviews """
    rating: float
    contents: str
    episode_id: str
    review_id: str

    def __init__(self, episode_id: str, rating: float, contents: str, review_id: str):
        self.episode_id = episode_id
        self.rating = rating
        self.contents = contents
        self.review_id = review_id
