from utils.orjson import orjson, orjson_dumps

from models.mixins import UUIDMixin
from models.actor import Actor
from models.director import Director
from models.writer import Writer
from models.genre import Genre


class Film(UUIDMixin):
    imdb_rating: str
    title: str
    description: str
    created_at: str
    directors: list[Director]
    actors_names: list[str]
    actors: list[Actor]
    writers_names: list[str]
    writers: list[Writer]
    genres: list[Genre]
    url: str

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
