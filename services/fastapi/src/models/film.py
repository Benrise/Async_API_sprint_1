from typing import List, Optional
from pydantic import BaseModel

from models.person import Person


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
        allow_population_by_field_name = True
