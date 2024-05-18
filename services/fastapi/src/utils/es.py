
def build_body(
    query: str = None,
    page: int = 0,
    size: int = 10,
    sort_order: str = None,
    sort_field: str = None,
    genre_id: str | None = None
) -> dict:
    bool_clause = {"must": [{"multi_match": {"query": query}}]} if query else {}
    sort_clause = {sort_field: {"order": sort_order} } if sort_order and sort_field else {}
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
