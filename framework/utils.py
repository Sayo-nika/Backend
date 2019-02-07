# External Libraries
from sqlalchemy import Query


def paginate(query: Query, page: int, limit: int = 50) -> Query:
    """Paginates a query, calculating the proper offset for the page"""
    return query.limit(limit).offset(page * limit)
