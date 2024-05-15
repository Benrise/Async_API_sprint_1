from models.person import Person
from models.genre import Genre

from typing import Optional, List
from pydantic import BaseModel
from typing_extensions import TypedDict


class Film(BaseModel):
    uuid: str
    title: str
    imdb_rating: Optional[float]
    description: Optional[str]
    directors: Optional[List[Person]]
    genres: Optional[List[Genre]]
    actors: Optional[List[Person]]
    writers: Optional[List[Person]]


class RoleID(TypedDict):
    uuid = str
    roles = List[str]


id_role_dict = TypedDict('RoleID', {'uuid': str, 'roles': List[str]})


class Person(BaseModel):
    uuid: str
    full_name: str


class PersonFilms(BaseModel):
    uuid: str
    full_name: str
    films: List[id_role_dict]


class FilmRating(BaseModel):
    uuid: str
    title: str
    imdb_rating: float


class Genre(BaseModel):
    uuid: str
    name: str
