from typing import Dict, Optional


def build_body(
    query: str,
    page: int,
    size: int,
    sort_order: str = 'desc',
    sort_field: str = 'imdb_rating',
    genre: Optional[str] = None
) -> Dict:
    bool_clause = {"must": [{"multi_match": {"query": query}}]} if query else {}
    sort_clause = {
        sort_field: {"order": sort_order}
    }
    if genre:
        bool_clause["filter"] = [{"term": {"genre.keyword": genre}}]

    return {
        "query": {"bool": bool_clause},
        "sort": sort_clause,
        "from": page,
        "size": size
    }
