from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from uuid import UUID

from typing_extensions import TypedDict
from typing import Optional, List

from services.person import PersonService, get_person_service

import core.config as config


router = APIRouter()


# Модель ответа API (не путать с моделью данных)

class RoleID(TypedDict):
    uuid = UUID
    roles = List[str]


id_role_dict = TypedDict('RoleID', {'uuid': UUID, 'roles': List[str]})


class Person(BaseModel):
    uuid: UUID
    full_name: str
    films: List[id_role_dict]


@router.get('/{person_id}',
            response_model=Person,
            summary='Получить информацию о жанре людях по его uuid',
            description='''
                Формат данных ответа:
                        uuid,
                        full_name,
                        films
                    ''')
async def person_details(person_id: str, person_service: PersonService = Depends(get_person_service)) -> Person:
    person = await person_service.get_by_id(person_id)
    if not person:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='person not found')
    return Person(uuid=person.uuid, full_name=person.full_name, films=person.films)
