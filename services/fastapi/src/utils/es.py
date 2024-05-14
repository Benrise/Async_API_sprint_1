from typing import Dict, Optional


def build_body(
    query: str,
    page: int,
    size: int,
    sort_order: str = 'desc',
    sort_field: str = 'imdb_rating',
    genre_id: Optional[str] = None
) -> Dict:
    bool_clause = {"must": [{"multi_match": {"query": query}}]} if query else {}
    sort_clause = {
        sort_field: {"order": sort_order}
    }
    if genre_id:
        bool_clause.setdefault("filter", []).append({"nested": {
            "path": "genres",
            "query": {
                "bool": {
                    "must": [{"match": {"genres.uuid": genre_id}}]
                }
            }
        }})

    return {
        "query": {"bool": bool_clause},
        "sort": sort_clause,
        "from": page,
        "size": size
    }
