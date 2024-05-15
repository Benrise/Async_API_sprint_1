from pydantic import BaseModel
from uuid import UUID
from typing_extensions import TypedDict
from typing import List


class RoleID(TypedDict):
    uuid = str
    roles = List[str]


id_role_dict = TypedDict('RoleID', {'uuid': str, 'roles': List[str]})


class Person(BaseModel):
    uuid: str
    full_name: str
    films: List[id_role_dict]
