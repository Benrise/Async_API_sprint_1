from functools import lru_cache

from http import HTTPStatus

import orjson

from elasticsearch import AsyncElasticsearch, NotFoundError, BadRequestError

from fastapi import Depends, HTTPException
from fastapi.encoders import jsonable_encoder

from redis.asyncio import Redis

from db.elastic import get_elastic
from db.redis import get_redis

from models.film import FilmModel, FilmRating


FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class FilmService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, film_id: str) -> FilmModel | None:
        film = await self._film_from_cache(film_id)
        if not film:
            film = await self._get_film_from_elastic(film_id)
            if not film:
                return None
            await self._put_film_to_cache(film)
        return film

    async def _get_film_from_elastic(self, film_id: str) -> FilmModel | None:
        try:
            doc = await self.elastic.get(index='movies', id=film_id)
        except NotFoundError:
            return None
        return FilmModel(**doc['_source'])

    async def _film_from_cache(self, film_id: str) -> FilmModel | None:
        data = await self.redis.get(film_id)
        if not data:
            return None
        film = FilmModel.model_validate_json(data)
        return film

    async def _put_film_to_cache(self, film: FilmModel):
        await self.redis.set(film.uuid, film.model_dump_json(), FILM_CACHE_EXPIRE_IN_SECONDS)

    async def get_by_query(self, query: str, page: int, size: int) -> FilmRating | None:
        word = query.lower()
        cache_key = f'film:query:{word}'
        films = await self._films_from_cache(cache_key)
        if not films:
            films = await self._get_films_by_query(query, page, size)
            if not films:
                return None
            await self._put_films_to_cache(films, cache_key)
        return films
    
    async def _get_films_by_query(self, query: str, page: int, size: int) -> FilmRating | None:
        page -= 1
        body = {"from": page, "size": size, "query": {"match": {"title": {"query": query}}}}
        try:
            doc = await self.elastic.search(index='movies',
                                            body=body,
                                            _source_includes=['uuid', 'title', 'imdb_rating'])
        except NotFoundError:
            return None
        return [FilmRating(**i['_source']) for i in doc['hits']['hits']]

    async def get_films(
            self, genre: str, sort_field: str, sort_order: str,  page: int, size: int
        ) -> list[FilmRating]:
        cache_key = 'film:rating:all'
        if genre:
            cache_key = f'film:rating:genre:{genre}'
        films = await self._films_from_cache(cache_key)
        if not films:
            films = await self._get_films_from_elastic(genre, sort_field,
                                                       sort_order, page, size)
            if not films:
                return None
            await self._put_films_to_cache(films, cache_key)
        return films

    async def _get_films_from_elastic(
            self, genre: str, sort_field: str, sort_order: str,  page: int, size: int
        ) -> list[FilmRating] | None:
        sort = sort_order.value
        page -= 1
        body = {"from": page, "size": size, "sort": {sort_field: {"order": sort}}}
        if genre:
            body["query"] = {
                "nested": {
                    "path": "genres","query": {
                        "bool": {"must": [{"match": {"genres.uuid": genre}},]}
                    },
                }
            }
        try:
            response = await self.elastic.search(index='movies',
                                                 body=body,
                                                 _source_includes=['uuid', 'title', 'imdb_rating'])
            films = [FilmRating(**doc['_source']) for doc in response['hits']['hits']]
        except NotFoundError:
            return None
        except BadRequestError:
            raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail='no matching sort field')
        return films

    async def _films_from_cache(self, cache_key: str) -> list[FilmRating] | None:
        films = await self.redis.get(cache_key)
        if not films:
            return None
        return [FilmRating(uuid=film['uuid'],
                           title=film['title'],
                           imdb_rating=film['imdb_rating']) for film in orjson.loads(films)]

    async def _put_films_to_cache(self, films: list[FilmRating], cache_key: str):
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
