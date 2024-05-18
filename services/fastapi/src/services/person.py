import orjson

from functools import lru_cache

from elasticsearch import AsyncElasticsearch, NotFoundError

from fastapi import Depends
from fastapi.encoders import jsonable_encoder

from redis.asyncio import Redis

from db.elastic import get_elastic
from db.redis import get_redis

from models.person import PersonFilms
from models.film import FilmRating

from utils.es import build_body

PERSON_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class PersonService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, person_id: str) -> PersonFilms | None:
        person = await self._person_from_cache(person_id)
        if not person:
            person = await self._get_person_from_elastic(person_id)
            if not person:
                return None
            await self._put_person_to_cache(person)
        return person

    async def _get_person_from_elastic(self, person_id: str) -> PersonFilms | None:
        try:
            doc = await self.elastic.get(index='persons', id=person_id)
        except NotFoundError:
            return None
        return PersonFilms(**doc['_source'])

    async def _person_from_cache(self, person_id: str) -> PersonFilms | None:
        data = await self.redis.get(person_id)
        if not data:
            return None

        person = PersonFilms.model_validate_json(data)
        return person

    async def _put_person_to_cache(self, person: PersonFilms):
        await self.redis.set(person.uuid, person.model_dump_json(), PERSON_CACHE_EXPIRE_IN_SECONDS)

    async def get_persons(self, query: str, page: int, size: int) -> list[PersonFilms]:
        page -= 1
        es_body = build_body(query, page, size)
        word = query.lower()
        cache_key = f'persons:query:{word}'
        persons = await self._persons_from_cache(cache_key)
        if persons:
            return persons
        persons = await self._get_persons_from_elastic(es_body)
        if not persons:
            return []
        await self._put_persons_to_cache(persons, cache_key)
        return persons

    async def _get_persons_from_elastic(self, body) -> list[PersonFilms] | None:
        try:
            response = await self.elastic.search(index='persons', body=body)
        except NotFoundError:
            return None
        persons = [PersonFilms(**doc['_source']) for doc in response['hits']['hits']]
        return persons

    async def _persons_from_cache(self, cache_key: str) -> list[PersonFilms] | None:
        persons: list[PersonFilms] = await self.redis.get(cache_key)
        if not persons:
            return None
        return orjson.loads(persons)

    async def _put_persons_to_cache(self, persons: list[PersonFilms], cache_key: str):
        await self.redis.set(
            cache_key,
            orjson.dumps(jsonable_encoder(persons)),
            PERSON_CACHE_EXPIRE_IN_SECONDS
        )

    async def get_person_film_rating(self, person_id: str) -> FilmRating | None:
        person_film_rating = await self._get_films_by_person(person_id)
        if not person_film_rating:
            return None
        return person_film_rating

    async def _get_films_by_person(self, person_id) -> FilmRating | None:
        sorting = {"imdb_rating": {"order": "desc"}}
        try:
            doc = await self.elastic.search(index='persons',
                                            body={"query": {"match": {"uuid": {"query": person_id}}}},
                                            _source_includes=['films.uuid',])

            film_ids = [i['_source']['films'] for i in doc['hits']['hits']][0]
            ids = [id['uuid'] for id in film_ids]

            doc_movies = await self.elastic.search(index='movies',
                                                   body={
                                                       "query": {"ids": {"values": ids}},
                                                       "sort": sorting, "from": 0, "size": 100
                                                   },
                                                   _source_includes=['uuid', 'title', 'imdb_rating'])
            ratings = [FilmRating(**i['_source']) for i in doc_movies['hits']['hits']]
        except NotFoundError:
            return None
        return ratings

@lru_cache()
def get_person_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)
