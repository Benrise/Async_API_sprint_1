from http import HTTPStatus
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from models.person import Person

from services.genre import GenreService, get_genre_service

import core.config as config


router = APIRouter()


# Модель ответа API (не путать с моделью данных)
class Genre(BaseModel):
    uuid: str
    name: str


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
