from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Query

from services.person import PersonService, get_person_service
import core.config as config
from models.person import PersonFilms
from models.film import FilmRating

router = APIRouter()


@router.get('/{person_id}',
            response_model=PersonFilms,
            summary='Получить информацию о жанре людях по его uuid',
            description='''
                Формат данных ответа:
                        uuid,
                        full_name,
                        films
                    ''')
async def person_details(person_id: str, person_service: PersonService = Depends(get_person_service)) -> PersonFilms:
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='person not found')
    return PersonFilms(uuid=person.uuid, full_name=person.full_name, films=person.films)


@router.get('/search/',
            response_model=list[PersonFilms],
            defautlt='Lucas',
            summary='Получить список людей',
            description='Формат массива данных ответа: uuid, full_name, films')
async def persons_list(
        query: str = Query(
            default=None,
            alias=config.QUERY_ALIAS,
            description=config.QUERY_DESC
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
        person_service: PersonService = Depends(get_person_service)) -> list[PersonFilms]:
    persons = await person_service.get_persons(
        query,
        page,
        size,
    )
    if not persons:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='persons not found')
    return persons


@router.get('/{person_id}/film', response_model=list[FilmRating])
async def person_by_films(person_id: str, person_service: PersonService = Depends(get_person_service)) -> list[FilmRating]:
    person_films = await person_service.get_person_film_rating(person_id)
    if not person_films:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='person not found')

    return [FilmRating(uuid=person_id, title=p_film.title, imdb_rating=p_film.imdb_rating) for p_film in person_films]