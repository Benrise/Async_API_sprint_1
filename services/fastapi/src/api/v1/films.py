import core.config as config

from http import HTTPStatus
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query

from services.film import FilmService, get_film_service
from utils.enums import Sort
from .schema import Film


router = APIRouter()


@router.get('/{film_id}',
            response_model=Film,
            summary='Получить информацию о фильме по его uuid',
            description='''
                Формат данных ответа:
                        uuid,
                        title,
                        imdb_rating,
                        description,
                        genre,
                        actors,
                        writers,
                        directors
                    ''')
async def film_details(film_id: str, film_service: FilmService = Depends(get_film_service)) -> Film:
    film = await film_service.get_by_id(film_id)
    if not film:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='film not found')
    return Film(uuid=film.uuid,
                title=film.title,
                imdb_rating=film.imdb_rating,
                description=film.description,
                genres=film.genres,
                actors=film.actors,
                writers=film.writers,
                directors=film.directors)


@router.get('',
            response_model=List[Film],
            summary='Получить список фильмов',
            description='Формат массива данных ответа: uuid, title, imdb_rating, description, genre, actors, writers, directors')
async def films_list(
        query: str = Query(
            default=None,
            alias=config.QUERY_ALIAS,
            description=config.QUERY_DESC
        ),
        sort_order: Sort = Query(
            default=Sort.desc.name,
            alias=config.SORT_ORDER_ALIAS,
            description=config.SORT_ORDER_DESC
        ),
        sort_field: str = Query(
            default='imdb_rating',
            alias=config.SORT_FIELD_ALIAS,
            description=config.SORT_FIELD_DESC,
        ),
        page: int = Query(
            default=1,
            ge=1,
            alias=config.PAGE_ALIAS,
            description=config.PAGE_DESC
        ),
        size: int = Query(
            default=10,
            ge=1,
            le=config.MAX_PAGE_SIZE,
            alias=config.SIZE_ALIAS,
            description=config.SIZE_DESC
        ),
        genre: str = Query(
            default=None,
            alias=config.GENRE_ALIAS,
            description=config.GENRE_DESC
        ),
        film_service: FilmService = Depends(get_film_service)) -> List[Film]:
    films = await film_service.get_films(
        query,
        sort_order,
        sort_field,
        page,
        size,
        genre
    )
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='films not found')
    return films
