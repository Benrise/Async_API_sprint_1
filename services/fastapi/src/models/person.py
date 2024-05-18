from pydantic import BaseModel
from typing_extensions import TypedDict


id_role_dict = TypedDict('RoleID', {'uuid': str, 'roles': list[str]})


class Person(BaseModel):
    uuid: str
    full_name: str


class PersonFilms(Person):
    films: list[id_role_dict]
