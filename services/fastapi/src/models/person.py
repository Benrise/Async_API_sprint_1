from pydantic import BaseModel
from typing_extensions import TypedDict
from typing import List, Optional


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
