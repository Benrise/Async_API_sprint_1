from pydantic import BaseModel

from models.person import Person
from models.genre import Genre


class FilmRating(BaseModel):
    uuid: str
    title: str
    imdb_rating: float | None = None


class Film(FilmRating):
    description: str | None = None
    genres: list[Genre] | None = None
    actors: list[Person] | None = None
    writers: list[Person] | None = None
    directors: list[Person] | None = None


class FilmModel(Film):
    class Config:
        allow_population_by_field_name = True
