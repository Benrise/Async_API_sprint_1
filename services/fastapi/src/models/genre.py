from pydantic import BaseModel


class Genre(BaseModel):
    uuid: str
    name: str

    class Config:
        allow_population_by_field_name = True
