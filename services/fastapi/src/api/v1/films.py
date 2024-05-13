from http import HTTPStatus
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from models.person import Person

from services.film import FilmService, get_film_service


router = APIRouter()


# Модель ответа API (не путать с моделью данных)
class Film(BaseModel):
    id: str
    title: str
    imdb_rating: Optional[float]
    description: Optional[str]
    directors: Optional[List[Person]]
    genres: Optional[List[str]]
    actors: Optional[List[Person]]
    writers: Optional[List[Person]]


@router.get('/{film_id}',
            response_model=Film,
            summary='Получить информацию о фильме по его id',
            description='Формат данных ответа: id, title, imdb_rating, description, genre, actors, writers, directors')
async def film_details(film_id: str, film_service: FilmService = Depends(get_film_service)) -> Film:
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='film not found')
    return Film(id=film.id,
                title=film.title,
                imdb_rating=film.imdb_rating,
                description=film.description,
                genres=film.genres,
                actors=film.actors,
                writers=film.writers,
                directors=film.directors)
