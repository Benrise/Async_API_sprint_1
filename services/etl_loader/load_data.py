import os
import sys
import json

from typing import List
from elasticsearch import Elasticsearch

from utils.logger import logger

from process.elasticloader import ElasticLoader
from dotenv import load_dotenv

load_dotenv('./env/dev/.env', override=False)

ELASTIC_PROTOCOL = os.getenv('ELASTIC_PROTOCOL', 'http')
ELASTIC_HOST = os.getenv('ELASTIC_HOST', '127.0.0.1')
ELASTIC_PORT = int(os.getenv('ELASTIC_PORT', 9200))


hosts = [f'{ELASTIC_PROTOCOL}://{ELASTIC_HOST}:{ELASTIC_PORT}']


def movie_loader(file: json, index: str) -> None:
    with open(file, encoding='utf8') as f:
        content = f.read()
        result = json.loads(content)
        for doc in result['hits']['hits']:
            data = doc['_source']
            es.add_movie(index, data)
    f.close()


def person_loader(file: json, index: str) -> None:
    with open(file, encoding='utf8') as f:
        content = f.read()
        result = json.loads(content)
        for doc in result['hits']['hits']:
            data = doc['_source']
            es.add_person(index, data)
    f.close()


def genre_loader(file: json, index: str) -> None:
    with open(file, encoding='utf8') as f:
        content = f.read()
        result = json.loads(content)
        for doc in result['hits']['hits']:
            data = doc['_source']
            es.add_genre(index, data)
    f.close()


def main(indices: List[tuple]) -> None:
    """The main method of loading data to Elasticsearch."""

    movies_index = indices[0][0]
    persons_index = indices[1][0]
    genres_index = indices[2][0]

    logger.info("Start loading data to Elasticsearch...")

    logger.info("Start movies...")
    movie_loader('docs/_search_movies.json', movies_index)
    logger.info("Movies Done")

    logger.info("Start persons...")
    person_loader('docs/_search_persons.json', persons_index)
    logger.info("Persons Done")

    logger.info("Start genres...")
    genre_loader('docs/_search_genres.json', genres_index)
    logger.info("Genres Done")

    logger.info("Done. All data was sent to Elasticsearch")


if __name__ == '__main__':

    client = Elasticsearch(hosts=hosts)
    es = ElasticLoader(client)

    indices = [
        ('movies', 'indices/movieIndex.json'),
        ('persons', 'indices/personIndex.json'),
        ('genres', 'indices/genreIndex.json')
    ]

    for idx in indices:
        create_index = es.create_index(*idx)

        if not create_index:
            logger.warning(f'The index {idx[0]} was not created.')
            sys.exit(1)

    main(indices)
