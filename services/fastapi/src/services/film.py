from functools import lru_cache
from typing import Optional, List

from http import HTTPStatus

import orjson

from elasticsearch import AsyncElasticsearch, NotFoundError, BadRequestError

from fastapi import Depends, HTTPException
from fastapi.encoders import jsonable_encoder

from redis.asyncio import Redis

from db.elastic import get_elastic
from db.redis import get_redis

from models.film import Fil
from utils.es import build_body


FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class FilmService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, film_id: str) -> Optional[Film]:
        film = await self._film_from_cache(film_id)
        if not film:
            film = await self._get_film_from_elastic(film_id)
            if not film:
                return None
            await self._put_film_to_cache(film)

        return film

    async def _get_film_from_elastic(self, film_id: str) -> Optional[Film]:
        try:
            doc = await self.elastic.get(index='movies', id=film_id)
        except NotFoundError:
            return None
        return Film(**doc['_source'])

    async def _film_from_cache(self, film_id: str) -> Optional[Film]:
        data = await self.redis.get(film_id)
        if not data:
            return None

        film = Film.model_validate_json(data)
        return film

    async def _put_film_to_cache(self, film: Film):
        await self.redis.set(film.uuid, film.model_dump_json(), FILM_CACHE_EXPIRE_IN_SECONDS)

    async def get_films(
                self,
                query: str,
                sort_order: str,
                sort_field: str,
                page: int,
                size: int,
                genre: str
            ) -> List[Film]:
        page = page - 1
        es_body = build_body(query, page, size, sort_order, sort_field, genre)
        cache_key = f'films:{query}:{sort_order}:{sort_field}:{page}:{size}:{genre}'
        films = await self._films_from_cache(cache_key)
        if films:
            return films
        films = await self._get_films_from_elastic(es_body)
        if not films:
            return []
        await self._put_films_to_cache(films, cache_key)
        return films

    async def _get_films_from_elastic(self, body: dict) -> Optional[List[Film]]:
        try:
            response = await self.elastic.search(index='movies', body=body)
        except NotFoundError:
            return None
        except BadRequestError:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='no matching sort field')
        films = [Film(**doc['_source']) for doc in response['hits']['hits']]
        return films

    async def _films_from_cache(self, cache_key: str) -> Optional[List[Film]]:
        films: List[Film] = await self.redis.get(cache_key)
        if not films:
            return None
        return orjson.loads(films)

    async def _put_films_to_cache(self, films: List[Film], cache_key: str):
        await self.redis.set(
            cache_key,
            orjson.dumps(jsonable_encoder(films)),
            FILM_CACHE_EXPIRE_IN_SECONDS
        )


@lru_cache()
def get_film_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)
