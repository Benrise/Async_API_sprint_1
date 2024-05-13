from models.mixins import UUIDMixin


class Person(UUIDMixin):
    full_name: str
