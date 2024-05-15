from typing import List, Optional
from pydantic import BaseModel

from models.person import Person
from models.genre import Genre


class Film(BaseModel):
    uuid: str
    imdb_rating: Optional[float]
    title: str
    genres: Optional[List[Genre]]
    description: Optional[str]
    directors: Optional[List[Person]]
    actors: Optional[List[Person]]
    writers: Optional[List[Person]]

    class Config:
        allow_population_by_field_name = True


class FilmRating(BaseModel):
    uuid: str
    title: str
    imdb_rating: float
