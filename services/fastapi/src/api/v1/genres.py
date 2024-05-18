import core.config as config

from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException

from services.genre import GenreService, get_genre_service
#from .schema import Genre
from models.genre import Genre


router = APIRouter()


@router.get('/{genre_id}',
            response_model=Genre,
            summary='Получить информацию о жанре по его uuid',
            description='''
                Формат данных ответа:
                        uuid,
                        name,
                    ''')
async def film_details(genre_id: str, genre_service: GenreService = Depends(get_genre_service)) -> Genre:
    genre = await genre_service.get_by_id(genre_id)
    if not genre:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='genre not found')
    return Genre(uuid=genre.uuid, name=genre.name)


@router.get('',
            response_model=list[Genre],
            summary='Получить список жанров',
            description='Формат массива данных ответа: uuid, name, ')
async def genre_list(film_service: GenreService = Depends(get_genre_service)) -> list[Genre]:
    films = await film_service.get_genres(size=config.MAX_GENRES_SIZE)
    if not films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='genres not found')
    return films
