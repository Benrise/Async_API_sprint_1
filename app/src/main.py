import logging

from contextlib import asynccontextmanager

import uvicorn
from elasticsearch import AsyncElasticsearch
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from redis.asyncio import Redis

from api.v1 import films

from core import config
from core.logger import LOGGING
from db import elastic
from db import redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Будет выполнено до запуска приложения
    # Подключаемся к базам при старте сервера
    # Подключиться можем при работающем event-loop
    # Поэтому логика подключения происходит в асинхронной функции
    redis.redis = Redis(host=config.REDIS_HOST, port=config.REDIS_PORT)
    elastic.es = AsyncElasticsearch(
        hosts=[f'{config.ELASTIC_PROTOCOL}://{config.ELASTIC_HOST}:{config.ELASTIC_PORT}']
    )
    yield
    # Будет выполнено после закрытия приложения
    # Отключаемся от баз при выключении сервера
    await redis.redis.close()
    await elastic.es.close()

app = FastAPI(
    # Конфигурируем название проекта. Оно будет отображаться в документации
    title=config.PROJECT_NAME,
    # Адрес документации в красивом интерфейсе
    docs_url='/api/openapi',
    # Адрес документации в формате OpenAPI
    openapi_url='/api/openapi.json',
    # Можно сразу сделать небольшую оптимизацию сервиса 
        # и заменить стандартный JSON-сереализатор на более шуструю версию, написанную на Rust
    default_response_class=ORJSONResponse,
    # Функция жизненного цикла приложения
    lifespan=lifespan
)

# Подключаем роутер к серверу, указав префикс /v1/films
# Теги указываем для удобства навигации по документации
app.include_router(films.router, prefix='/api/v1/films', tags=['films'])

if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8000,
        log_config=LOGGING,
        log_level=logging.DEBUG,
    )