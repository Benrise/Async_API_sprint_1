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

    async def get_persons(self, query: str, page: int, size: int) -> List[Person]:
        es_body = build_body(query, page, size)
        cache_key = f'persons:{query}:{page}:{size}'
        persons = await self._persons_from_cache(cache_key)
        if persons:
            return persons
        persons = await self._get_persons_from_elastic(es_body)
        if not persons:
            return []
        await self._put_persons_to_cache(persons, cache_key)
        return persons

    async def _get_persons_from_elastic(self, body) -> Optional[List[Person]]:
        try:
            response = await self.elastic.search(index='persons', body=body)
        except NotFoundError:
            return None
        persons = [Person(**doc['_source']) for doc in response['hits']['hits']]
        return persons

    async def _persons_from_cache(self, cache_key: str) -> Optional[List[Person]]:
        persons: List[Person] = await self.redis.get(cache_key)
        if not persons:
            return None
        return orjson.loads(persons)

    async def _put_persons_to_cache(self, persons: List[Person], cache_key: str):
        await self.redis.set(
            cache_key,
            orjson.dumps(jsonable_encoder(persons)),
            PERSON_CACHE_EXPIRE_IN_SECONDS
        )


@lru_cache()
def get_person_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)
