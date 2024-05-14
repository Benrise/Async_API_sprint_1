import json
from utils.logger import logger

from elasticsearch import Elasticsearch
from typing import Any, Dict, Text


class ElasticLoader:
    """Class to load data to Elasticseach."""
    def __init__(self, client: object) -> None:
        self.client = client

    def create_index(self, index: str, index_data: Text) -> bool:
        """Method to create an index in Elasticsearch."""

        if self.client.ping():
            logger.info(
                'Response received successfully. Elastichsearch is working.'
            )
            
            exists_index = self.client.indices.exists(index=index)

            if not exists_index:
                with open(index_data, 'r') as file:
                    data = file.read()
                    idx = json.loads(data)
                    settings = idx['settings']
                    mappings = idx['mappings']

                create_index = self.client.indices.create(
                    index=index, settings=settings, mappings=mappings
                )
                if create_index['acknowledged']:
                    logger.info(
                        f'The index {index} was successfully created.'
                    )
            else:
                logger.info(f'The index {index} already exists.')
            return True
        else:
            logger.warning(
                'The request could not be made. Elasticsearch is not working.'
            )
            return False

    def _check_doc_exists(self, index: str, id: str) -> bool:
        """
        Private method to check the existence of the
        document in Elastichsearch.

        Return True if exists, otherwise False.
        """
        check = self.client.exists(index=index, id=id)
        return check

    def add_movie(self, index: str, data: Dict[str, Any]) -> None:
        """Method to create a film."""
        id = data['uuid']
        title = data['title']
        rating = 0.0 if not data['imdb_rating'] else data['imdb_rating']
        rating = float(rating)
        description = data['description']
        genres = list(data['genres'])
        actors = data['actors']
        writers = data['writers']
        directors = data['directors']

        if not self._check_doc_exists(index, id):
            self.client.index(
                index=index,
                id=id,
                body={
                    "uuid": f"{id}",
                    "title": f"{title}",
                    "imdb_rating": f"{rating}",
                    "description": f"{description}",
                    "genres": genres,
                    "actors": actors,
                    "writers": writers,
                    "directors": directors
                },
            )

    def add_person(self, index: str, data: Dict[str, Any]) -> None:
        """Add all information about the persons."""
        person_id = data['uuid']
        name = data['full_name']
        films = data['films']

        if not self._check_doc_exists(index, person_id):
            self.client.index(
                index=index,
                id=person_id,
                body={
                    "uuid": f"{person_id}",
                    "full_name": f"{name}",
                    "films": films
                },
            )

    def add_genre(self, index: str, data: Dict[str, Any]) -> None:
        """Method to add all ralated data to genres."""
        genre_id = data['uuid']
        genre = data['name']

        if not self._check_doc_exists(index, genre_id):
            self.client.index(
                index=index,
                id=genre_id,
                body={
                    "uuid": f"{genre_id}",
                    "name": f"{genre}",
                },
            )
