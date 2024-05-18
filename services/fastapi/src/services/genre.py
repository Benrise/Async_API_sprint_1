import orjson

from functools import lru_cache

from elasticsearch import AsyncElasticsearch, NotFoundError

from fastapi import Depends
from fastapi.encoders import jsonable_encoder

from redis.asyncio import Redis

from db.elastic import get_elastic
from db.redis import get_redis

from models.genre import GenreModel

from utils.es import build_body


GENRE_CACHE_EXPIRE_IN_SECONDS = 60 * 5


class GenreService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    async def get_by_id(self, genre_id: str) -> GenreModel | None:
        genre = await self._genre_from_cache(genre_id)
        if not genre:
            genre = await self._get_genre_from_elastic(genre_id)
            if not genre:
                return None
            await self._put_genre_to_cache(genre)
        return genre

    async def _get_genre_from_elastic(self, genre_id: str) -> GenreModel | None:
        try:
            doc = await self.elastic.get(index='genres', id=genre_id)
        except NotFoundError:
            return None
        return GenreModel(**doc['_source'])

    async def _genre_from_cache(self, genre_id: str) -> GenreModel | None:
        data = await self.redis.get(genre_id)
        if not data:
            return None

        Genre = GenreModel.model_validate_json(data)
        return Genre

    async def _put_genre_to_cache(self, Genre: GenreModel):
        await self.redis.set(Genre.uuid, Genre.model_dump_json(), GENRE_CACHE_EXPIRE_IN_SECONDS)

    async def get_genres(self, size: int) -> list[GenreModel]:
        cache_key = 'genre:all'
        body = build_body(size=size)
        genres = await self._genres_from_cache(cache_key)
        if genres:
            return genres
        genres = await self._get_genres_from_elastic(body)
        if not genres:
            return []
        await self._put_genres_to_cache(genres, cache_key)
        return genres

    async def _get_genres_from_elastic(self, body) -> list[GenreModel] | None:
        try:
            response = await self.elastic.search(index='genres', body=body)
        except NotFoundError:
            return None
        genres = [GenreModel(**doc['_source']) for doc in response['hits']['hits']]
        return genres

    async def _genres_from_cache(self, cache_key: str) -> list[GenreModel] | None:
        genres: list[GenreModel] = await self.redis.get(cache_key)
        if not genres:
            return None
        return orjson.loads(genres)

    async def _put_genres_to_cache(self, genres: list[GenreModel], cache_key: str):
        await self.redis.set(
            cache_key,
            orjson.dumps(jsonable_encoder(genres)),
            GENRE_CACHE_EXPIRE_IN_SECONDS
        )


@lru_cache()
def get_genre_service(
        redis: Redis = Depends(get_redis),
        elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(redis, elastic)
