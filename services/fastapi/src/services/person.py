from functools import lru_cache
from typing import Optional, List

from http import HTTPStatus

from elasticsearch import AsyncElasticsearch, NotFoundError, BadRequestError

from fastapi import Depends, HTTPException
from fastapi.encoders import jsonable_encoder

from redis.asyncio import Redis

import orjson

from db.elastic import get_elastic
from db.redis import get_redis

from models.person import Person

from utils.es import build_body


PERSON_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class PersonService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, person_id: str) -> Optional[Person]:
        person = await self._person_from_cache(person_id)
        if not person:
            person = await self._get_person_from_elastic(person_id)
            if not person:
                return None
            await self._put_person_to_cache(person)

        return person

    async def _get_person_from_elastic(self, person_id: str) -> Optional[Person]:
        try:
            doc = await self.elastic.get(index='persons', id=person_id)
        except NotFoundError:
            return None
        return Person(**doc['_source'])

    async def _person_from_cache(self, person_id: str) -> Optional[Person]:
        data = await self.redis.get(person_id)
        if not data:
            return None

        person = Person.model_validate_json(data)
        return person

    async def _put_person_to_cache(self, person: Person):
        await self.redis.set(person.uuid, person.model_dump_json(), PERSON_CACHE_EXPIRE_IN_SECONDS)


@lru_cache()
def get_person_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)
