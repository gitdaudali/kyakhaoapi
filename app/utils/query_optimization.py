"""Query optimization utilities to prevent N+1 queries and improve performance."""

from typing import List, Type, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload, Load


def with_relations(
    query,
    *relations: str,
    strategy: str = "selectin",
) -> select:
    """
    Add eager loading for relations to prevent N+1 queries.
    
    Args:
        query: SQLAlchemy select statement
        *relations: Relation names to eagerly load
        strategy: Loading strategy - "selectin" (default) or "joined"
        
    Returns:
        Query with eager loading options
        
    Example:
        stmt = select(Dish)
        stmt = with_relations(stmt, "moods", "restaurant", "cuisine")
    """
    if strategy == "selectin":
        loader = selectinload
    elif strategy == "joined":
        loader = joinedload
    else:
        raise ValueError(f"Invalid strategy: {strategy}. Use 'selectin' or 'joined'")
    
    for relation in relations:
        query = query.options(loader(relation))
    
    return query


def optimize_dish_query(query, include_all: bool = True) -> select:
    """
    Optimize dish query with common relations.
    
    Args:
        query: Base dish query
        include_all: Include all common relations (moods, restaurant, cuisine)
        
    Returns:
        Optimized query with eager loading
    """
    if include_all:
        return with_relations(
            query,
            "moods",
            "restaurant",
            "cuisine",
            strategy="selectin",
        )
    return query


def optimize_restaurant_query(query, include_dishes: bool = False) -> select:
    """
    Optimize restaurant query with relations.
    
    Args:
        query: Base restaurant query
        include_dishes: Whether to include dishes (use with caution - can be large)
        
    Returns:
        Optimized query with eager loading
    """
    if include_dishes:
        return with_relations(query, "dishes", strategy="selectin")
    return query


def optimize_cuisine_query(query, include_dishes: bool = False) -> select:
    """
    Optimize cuisine query with relations.
    
    Args:
        query: Base cuisine query
        include_dishes: Whether to include dishes (use with caution - can be large)
        
    Returns:
        Optimized query with eager loading
    """
    if include_dishes:
        return with_relations(query, "dishes", strategy="selectin")
    return query


def batch_load_relations(
    session: AsyncSession,
    entities: List,
    relation_name: str,
) -> None:
    """
    Batch load a relation for multiple entities to prevent N+1.
    
    Args:
        session: Database session
        entities: List of entities
        relation_name: Name of relation to load
        
    Example:
        dishes = await session.execute(select(Dish))
        batch_load_relations(session, dishes.scalars().all(), "moods")
    """
    if not entities:
        return
    
    # Use selectinload to load relation for all entities at once
    from sqlalchemy.orm import selectinload
    
    # Get the model class from first entity
    model_class = type(entities[0])
    relation = getattr(model_class, relation_name)
    
    # Load relation for all entities
    entity_ids = [entity.id for entity in entities]
    stmt = (
        select(model_class)
        .options(selectinload(relation))
        .where(model_class.id.in_(entity_ids))
    )
    await session.execute(stmt)


class QueryOptimizer:
    """Helper class for query optimization patterns."""

    @staticmethod
    def prevent_n_plus_one(
        query,
        *relations: str,
        strategy: str = "selectin",
    ) -> select:
        """
        Prevent N+1 queries by adding eager loading.
        
        Args:
            query: SQLAlchemy query
            *relations: Relations to eagerly load
            strategy: Loading strategy
            
        Returns:
            Optimized query
        """
        return with_relations(query, *relations, strategy=strategy)

    @staticmethod
    def add_pagination(
        query,
        limit: int = 100,
        offset: int = 0,
    ) -> select:
        """
        Add pagination to query.
        
        Args:
            query: SQLAlchemy query
            limit: Maximum results
            offset: Skip results
            
        Returns:
            Query with pagination
        """
        return query.limit(limit).offset(offset)

    @staticmethod
    def add_ordering(
        query,
        *order_by,
        nulls_last: bool = True,
    ) -> select:
        """
        Add ordering to query.
        
        Args:
            query: SQLAlchemy query
            *order_by: Columns to order by
            nulls_last: Put nulls last
            
        Returns:
            Query with ordering
        """
        if not order_by:
            return query
        
        for col in order_by:
            if nulls_last:
                query = query.order_by(col.desc().nullslast() if hasattr(col, 'desc') else col)
            else:
                query = query.order_by(col)
        
        return query

