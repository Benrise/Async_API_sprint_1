from typing import List, Optional
from pydantic import BaseModel

import orjson

from models.person import Person


def orjson_dumps(v, *, default):
    return orjson.dumps(v, default=default).decode()


class Film(BaseModel):
    id: str
    imdb_rating: Optional[float]
    title: str
    genres: List[str]
    description: Optional[str]
    directors: Optional[List[Person]]
    actors_names: Optional[List[str]]
    writers_names: Optional[List[str]]
    actors: Optional[List[Person]]
    writers: Optional[List[Person]]

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
        allow_population_by_field_name = True
