from models.film import Film
from models.person import Person


class Actor(Person):
    filmed_at: list[Film]
