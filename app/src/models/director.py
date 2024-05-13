from models.film import Film
from models.person import Person


class Director(Person):
    directed_at: list[Film]
