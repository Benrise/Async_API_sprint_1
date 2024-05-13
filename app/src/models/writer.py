from models.film import Film
from models.person import Person


class Writer(Person):
    wrote_at: list[Film]
