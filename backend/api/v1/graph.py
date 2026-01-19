"""
Graph API endpoints for knowledge graph operations with advanced visualization.

This module provides REST API endpoints for accessing and manipulating
the knowledge graph in the Raptorflow backend, including advanced
querying, pattern matching, and visualization capabilities.
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from backend.core.auth import get_current_user, get_workspace_id
from backend.core.models import User
from ...memory.graph_memory import GraphMemory
from ...memory.graph_models import (
    EntityType,
    GraphEntity,
    GraphRelationship,
    RelationType,
)
from ...memory.graph_query import GraphPattern, GraphQueryEngine
from ...memory.vector_store import VectorMemory

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/graph", tags=["graph"])


# Pydantic models for API requests/responses
class GraphEntityRequest(BaseModel):
    name: str = Field(..., description="Entity name")
    entity_type: str = Field(..., description="Entity type")
    properties: Optional[Dict[str, Any]] = Field(
        default={}, description="Entity properties"
    )
    workspace_id: str = Field(..., description="Workspace ID")


class GraphEntityResponse(BaseModel):
    id: str
    workspace_id: str
    entity_type: str
    name: str
    properties: Dict[str, Any]
    created_at: str
    updated_at: str


class GraphRelationshipRequest(BaseModel):
    source_id: str = Field(..., description="Source entity ID")
    target_id: str = Field(..., description="Target entity ID")
    relation_type: str = Field(..., description="Relationship type")
    properties: Optional[Dict[str, Any]] = Field(
        default={}, description="Relationship properties"
    )
    weight: float = Field(1.0, description="Relationship weight")
    workspace_id: str = Field(..., description="Workspace ID")


class GraphRelationshipResponse(BaseModel):
    id: str
    workspace_id: str
    source_id: str
    target_id: str
    relation_type: str
    properties: Dict[str, Any]
    weight: float
    created_at: str
    updated_at: str


class SubGraphResponse(BaseModel):
    entities: List[GraphEntityResponse]
    relationships: List[GraphRelationshipResponse]


class GraphQueryRequest(BaseModel):
    pattern: Dict[str, Any] = Field(..., description="Graph pattern to match")
    workspace_id: str = Field(..., description="Workspace ID")
    limit: int = Field(50, description="Maximum number of results")


# Dependency to get graph memory
async def get_graph_memory() -> GraphMemory:
    """Get graph memory instance."""
    return GraphMemory()


@router.get("/entities", response_model=List[GraphEntityResponse])
async def get_entities(
    workspace_id: str = Query(..., description="Workspace ID"),
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    name_pattern: Optional[str] = Query(None, description="Filter by name pattern"),
    limit: int = Query(50, description="Maximum number of results"),
    current_user: User = Depends(get_current_user),
    graph_memory: GraphMemory = Depends(get_graph_memory),
):
    """
    Get entities from the knowledge graph.

    Args:
        workspace_id: Workspace ID
        entity_type: Optional entity type filter
        name_pattern: Optional name pattern filter
        limit: Maximum number of results
        current_user: Authenticated user
        graph_memory: Graph memory instance

    Returns:
        List of entities
    """
    try:
        # Validate workspace access
        workspace = await get_workspace_access(workspace_id, current_user.id)

        # Convert entity type if provided
        target_type = None
        if entity_type:
            target_type = EntityType(entity_type)

        # Find entities
        entities = await graph_memory.find_entities(
            workspace_id=workspace_id,
            entity_type=target_type,
            name_regex=name_pattern,
            limit=limit,
        )

        # Convert to response format
        return [
            GraphEntityResponse(
                id=entity.id,
                workspace_id=entity.workspace_id,
                entity_type=entity.entity_type.value,
                name=entity.name,
                properties=entity.properties or {},
                created_at=entity.created_at.isoformat() if entity.created_at else "",
                updated_at=entity.updated_at.isoformat() if entity.updated_at else "",
            )
            for entity in entities
        ]

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting entities: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/entities", response_model=GraphEntityResponse)
async def create_entity(
    request: GraphEntityRequest,
    current_user: User = Depends(get_current_user),
    graph_memory: GraphMemory = Depends(get_graph_memory),
):
    """
    Create a new entity in the knowledge graph.

    Args:
        request: Entity creation request
        current_user: Authenticated user
        graph_memory: Graph memory instance

    Returns:
        Created entity
    """
    try:
        # Validate workspace access
        workspace = await get_workspace_access(request.workspace_id, current_user.id)

        # Create entity
        entity_id = await graph_memory.add_entity(
            workspace_id=request.workspace_id,
            entity_type=EntityType(request.entity_type),
            name=request.name,
            properties=request.properties,
        )

        # Get created entity
        entity = await graph_memory.get_entity(entity_id)

        return GraphEntityResponse(
            id=entity.id,
            workspace_id=entity.workspace_id,
            entity_type=entity.entity_type.value,
            name=entity.name,
            properties=entity.properties or {},
            created_at=entity.created_at.isoformat() if entity.created_at else "",
            updated_at=entity.updated_at.isoformat() if entity.updated_at else "",
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating entity: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/entities/{entity_id}", response_model=GraphEntityResponse)
async def get_entity(
    entity_id: str,
    workspace_id: str = Query(..., description="Workspace ID"),
    current_user: User = Depends(get_current_user),
    graph_memory: GraphMemory = Depends(get_graph_memory),
):
    """
    Get a specific entity by ID.

    Args:
        entity_id: Entity ID
        workspace_id: Workspace ID
        current_user: Authenticated user
        graph_memory: Graph memory instance

    Returns:
        Entity
    """
    try:
        # Validate workspace access
        workspace = await get_workspace_access(workspace_id, current_user.id)

        # Get entity
        entity = await graph_memory.get_entity(entity_id)

        if not entity:
            raise HTTPException(status_code=404, detail="Entity not found")

        return GraphEntityResponse(
            id=entity.id,
            workspace_id=entity.workspace_id,
            entity_type=entity.entity_type.value,
            name=entity.name,
            properties=entity.properties or {},
            created_at=entity.created_at.isoformat() if entity.created_at else "",
            updated_at=entity.updated_at.isoformat() if entity.updated_at else "",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting entity: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/entities/{entity_id}", response_model=GraphEntityResponse)
async def update_entity(
    entity_id: str,
    request: GraphEntityRequest,
    current_user: User = Depends(get_current_user),
    graph_memory: GraphMemory = Depends(get_graph_memory),
):
    """
    Update an entity in the knowledge graph.

    Args:
        entity_id: Entity ID
        request: Entity update request
        current_user: Authenticated user
        graph_memory: Graph memory instance

    Returns:
        Updated entity
    """
    try:
        # Validate workspace access
        workspace = await get_workspace_access(request.workspace_id, current_user.id)

        # Update entity
        await graph_memory.update_entity(
            entity_id=entity_id, name=request.name, properties=request.properties
        )

        # Get updated entity
        entity = await graph_memory.get_entity(entity_id)

        return GraphEntityResponse(
            id=entity.id,
            workspace_id=entity.workspace_id,
            entity_type=entity.entity_type.value,
            name=entity.name,
            properties=entity.properties or {},
            created_at=entity.created_at.isoformat() if entity.created_at else "",
            updated_at=entity.updated_at.isoformat() if entity.updated_at else "",
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating entity: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/entities/{entity_id}")
async def delete_entity(
    entity_id: str,
    workspace_id: str = Query(..., description="Workspace ID"),
    current_user: User = Depends(get_current_user),
    graph_memory: GraphMemory = Depends(get_graph_memory),
):
    """
    Delete an entity from the knowledge graph.

    Args:
        entity_id: Entity ID
        workspace_id: Workspace ID
        current_user: Authenticated user
        graph_memory: Graph memory instance

    Returns:
        Success message
    """
    try:
        # Validate workspace access
        workspace = await get_workspace_access(workspace_id, current_user.id)

        # Delete entity
        success = await graph_memory.delete_entity(entity_id)

        if not success:
            raise HTTPException(status_code=404, detail="Entity not found")

        return {"message": "Entity deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting entity: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get(
    "/entities/{entity_id}/relationships",
    response_model=List[GraphRelationshipResponse],
)
async def get_entity_relationships(
    entity_id: str,
    workspace_id: str = Query(..., description="Workspace ID"),
    direction: str = Query(
        "both", description="Relationship direction (incoming, outgoing, both)"
    ),
    current_user: User = Depends(get_current_user),
    graph_memory: GraphMemory = Depends(get_graph_memory),
):
    """
    Get relationships for an entity.

    Args:
        entity_id: Entity ID
        workspace_id: Workspace ID
        direction: Relationship direction
        current_user: Authenticated user
        graph_memory: Graph memory instance

    Returns:
        List of relationships
    """
    try:
        # Validate workspace access
        workspace = await get_workspace_access(workspace_id, current_user.id)

        # Get relationships
        relationships = await graph_memory.get_relationships(
            entity_id=entity_id, direction=direction
        )

        # Convert to response format
        return [
            GraphRelationshipResponse(
                id=rel.id,
                workspace_id=rel.workspace_id,
                source_id=rel.source_id,
                target_id=rel.target_id,
                relation_type=rel.relation_type.value,
                properties=rel.properties or {},
                weight=rel.weight,
                created_at=rel.created_at.isoformat() if rel.created_at else "",
                updated_at=rel.updated_at.isoformat() if rel.updated_at else "",
            )
            for rel in relationships
        ]

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting entity relationships: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/relationships", response_model=GraphRelationshipResponse)
async def create_relationship(
    request: GraphRelationshipRequest,
    current_user: User = Depends(get_current_user),
    graph_memory: GraphMemory = Depends(get_graph_memory),
):
    """
    Create a new relationship in the knowledge graph.

    Args:
        request: Relationship creation request
        current_user: Authenticated user
        graph_memory: Graph memory instance

    Returns:
        Created relationship
    """
    try:
        # Validate workspace access
        workspace = await get_workspace_access(request.workspace_id, current_user.id)

        # Create relationship
        rel_id = await graph_memory.add_relationship(
            source_id=request.source_id,
            target_id=request.target_id,
            relation_type=RelationType(request.relation_type),
            weight=request.weight,
            properties=request.properties,
        )

        # Get created relationship
        relationship = await graph_memory.get_relationship(rel_id)

        return GraphRelationshipResponse(
            id=relationship.id,
            workspace_id=relationship.workspace_id,
            source_id=relationship.source_id,
            target_id=relationship.target_id,
            relation_type=relationship.relation_type.value,
            properties=relationship.properties or {},
            weight=relationship.weight,
            created_at=(
                relationship.created_at.isoformat() if relationship.created_at else ""
            ),
            updated_at=(
                relationship.updated_at.isoformat() if relationship.updated_at else ""
            ),
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating relationship: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/subgraph", response_model=SubGraphResponse)
async def get_subgraph(
    workspace_id: str = Query(..., description="Workspace ID"),
    center_entity: str = Query(..., description="Center entity ID"),
    depth: int = Query(2, description="Graph depth"),
    limit: int = Query(50, description="Maximum number of entities"),
    current_user: User = Depends(get_current_user),
    graph_memory: GraphMemory = Depends(get_graph_memory),
):
    """
    Get a subgraph centered around an entity.

    Args:
        workspace_id: Workspace ID
        center_entity: Center entity ID
        depth: Graph depth
        limit: Maximum number of entities
        current_user: Authenticated user
        graph_memory: Graph memory instance

    Returns:
        Subgraph with entities and relationships
    """
    try:
        # Validate workspace access
        workspace = await get_workspace_access(workspace_id, current_user.id)

        # Get subgraph
        subgraph = await graph_memory.get_subgraph(
            workspace_id=workspace_id,
            center_entity=center_entity,
            depth=depth,
            limit=limit,
        )

        # Convert entities to response format
        entities = [
            GraphEntityResponse(
                id=entity.id,
                workspace_id=entity.workspace_id,
                entity_type=entity.entity_type.value,
                name=entity.name,
                properties=entity.properties or {},
                created_at=entity.created_at.isoformat() if entity.created_at else "",
                updated_at=entity.updated_at.isoformat() if entity.updated_at else "",
            )
            for entity in subgraph.entities
        ]

        # Convert relationships to response format
        relationships = [
            GraphRelationshipResponse(
                id=rel.id,
                workspace_id=rel.workspace_id,
                source_id=rel.source_id,
                target_id=rel.target_id,
                relation_type=rel.relation_type.value,
                properties=rel.properties or {},
                weight=rel.weight,
                created_at=rel.created_at.isoformat() if rel.created_at else "",
                updated_at=rel.updated_at.isoformat() if rel.updated_at else "",
            )
            for rel in subgraph.relationships
        ]

        return SubGraphResponse(entities=entities, relationships=relationships)

    except Exception as e:
        logger.error(f"Error getting subgraph: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/query", response_model=SubGraphResponse)
async def query_graph(
    request: GraphQueryRequest,
    current_user: User = Depends(get_current_user),
    graph_memory: GraphMemory = Depends(get_graph_memory),
):
    """
    Query the knowledge graph with a pattern.

    Args:
        request: Graph query request
        current_user: Authenticated user
        graph_memory: Graph memory instance

    Returns:
        Subgraph matching the pattern
    """
    try:
        # Validate workspace access
        workspace = await get_workspace_access(request.workspace_id, current_user.id)

        # Query graph
        subgraph = await graph_memory.query_pattern(
            workspace_id=request.workspace_id,
            regex=request.pattern,
            limit=request.limit,
        )

        # Convert entities to response format
        entities = [
            GraphEntityResponse(
                id=entity.id,
                workspace_id=entity.workspace_id,
                entity_type=entity.entity_type.value,
                name=entity.name,
                properties=entity.properties or {},
                created_at=entity.created_at.isoformat() if entity.created_at else "",
                updated_at=entity.updated_at.isoformat() if entity.updated_at else "",
            )
            for entity in subgraph.entities
        ]

        # Convert relationships to response format
        relationships = [
            GraphRelationshipResponse(
                id=rel.id,
                workspace_id=rel.workspace_id,
                source_id=rel.source_id,
                target_id=rel.target_id,
                relation_type=rel.relation_type.value,
                properties=rel.properties or {},
                weight=rel.weight,
                created_at=rel.created_at.isoformat() if rel.created_at else "",
                updated_at=rel.updated_at.isoformat() if rel.updated_at else "",
            )
            for rel in subgraph.relationships
        ]

        return SubGraphResponse(entities=entities, relationships=relationships)

    except Exception as e:
        logger.error(f"Error querying graph: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/types", response_model=List[str])
async def get_entity_types(current_user: User = Depends(get_current_user)):
    """
    Get available entity types.

    Args:
        current_user: Authenticated user

    Returns:
        List of entity types
    """
    try:
        return [entity_type.value for entity_type in EntityType]
    except Exception as e:
        logger.error(f"Error getting entity types: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/relationship-types", response_model=List[str])
async def get_relationship_types(current_user: User = Depends(get_current_user)):
    """
    Get available relationship types.

    Args:
        current_user: Authenticated user

    Returns:
        List of relationship types
    """
    try:
        return [rel_type.value for rel_type in RelationType]
    except Exception as e:
        logger.error(f"Error getting relationship types: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


# Advanced Graph Visualization Endpoints


@router.get("/graph/entities")
async def get_graph_entities(
    user: User = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id),
    entity_type: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = Query(None),
):
    """
    Get graph entities with optional filtering and search.

    Args:
        entity_type: Filter by entity type
        limit: Maximum number of results
        search: Search query for entity names
    """
    try:
        graph_memory = GraphMemory()

        # Get entities
        if entity_type:
            try:
                entity_type_enum = EntityType(entity_type)
                entities = await graph_memory.find_entities(
                    workspace_id, entity_type_enum
                )
            except ValueError:
                raise HTTPException(
                    status_code=400, detail=f"Invalid entity type: {entity_type}"
                )
        else:
            entities = await graph_memory.get_all_entities(workspace_id)

        # Apply search filter
        if search:
            search_lower = search.lower()
            entities = [
                entity for entity in entities if search_lower in entity.name.lower()
            ]

        # Apply limit
        entities = entities[:limit]

        return {
            "entities": [
                {
                    "id": entity.id,
                    "name": entity.name,
                    "type": entity.entity_type.value,
                    "properties": entity.properties,
                    "created_at": (
                        entity.created_at.isoformat() if entity.created_at else None
                    ),
                }
                for entity in entities
            ],
            "total": len(entities),
            "filters": {"entity_type": entity_type, "search": search, "limit": limit},
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving entities: {str(e)}"
        )


@router.get("/graph/entity/{entity_id}")
async def get_graph_entity(
    entity_id: str,
    user: User = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id),
):
    """
    Get detailed information about a specific graph entity.

    Args:
        entity_id: Entity ID to retrieve
    """
    try:
        graph_memory = GraphMemory()
        entity = await graph_memory.get_entity(entity_id, workspace_id)

        if not entity:
            raise HTTPException(status_code=404, detail="Entity not found")

        # Get relationships
        relationships = await graph_memory.get_relationships(entity_id, workspace_id)

        return {
            "entity": {
                "id": entity.id,
                "name": entity.name,
                "type": entity.entity_type.value,
                "properties": entity.properties,
                "created_at": (
                    entity.created_at.isoformat() if entity.created_at else None
                ),
            },
            "relationships": [
                {
                    "id": rel.id,
                    "type": rel.relation_type.value,
                    "source_id": rel.source_id,
                    "target_id": rel.target_id,
                    "weight": rel.weight,
                    "properties": rel.properties,
                    "created_at": (
                        rel.created_at.isoformat() if rel.created_at else None
                    ),
                }
                for rel in relationships
            ],
            "relationship_count": len(relationships),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving entity: {str(e)}"
        )


@router.get("/graph/subgraph")
async def get_subgraph(
    user: User = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id),
    center_entity: str = Query(...),
    depth: int = Query(2, ge=1, le=5),
    max_entities: int = Query(100, ge=10, le=500),
):
    """
    Get subgraph centered around an entity.

    Args:
        center_entity: Center entity ID
        depth: Maximum depth from center
        max_entities: Maximum number of entities
    """
    try:
        graph_memory = GraphMemory()
        query_engine = GraphQueryEngine(graph_memory, VectorMemory())

        subgraph = await query_engine.get_subgraph(
            workspace_id=workspace_id,
            center_entity_id=center_entity,
            depth=depth,
            max_entities=max_entities,
        )

        if not subgraph:
            raise HTTPException(status_code=404, detail="Subgraph not found")

        return {
            "center_entity": center_entity,
            "depth": depth,
            "subgraph": {
                "entity_count": len(subgraph.entities),
                "relationship_count": len(subgraph.relationships),
                "entities": [
                    {
                        "id": entity.id,
                        "name": entity.name,
                        "type": entity.entity_type.value,
                        "properties": entity.properties,
                    }
                    for entity in subgraph.entities
                ],
                "relationships": [
                    {
                        "id": rel.id,
                        "type": rel.relation_type.value,
                        "source_id": rel.source_id,
                        "target_id": rel.target_id,
                        "weight": rel.weight,
                        "properties": rel.properties,
                    }
                    for rel in subgraph.relationships
                ],
            },
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error retrieving subgraph: {str(e)}"
        )


@router.get("/graph/path")
async def find_path(
    user: User = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id),
    from_entity: str = Query(...),
    to_entity: str = Query(...),
    max_depth: int = Query(5, ge=1, le=10),
    weight_function: str = Query("shortest", regex="^(shortest|weighted|semantic)$"),
):
    """
    Find path between two entities.

    Args:
        from_entity: Starting entity ID
        to_entity: Target entity ID
        max_depth: Maximum search depth
        weight_function: Path weight function
    """
    try:
        graph_memory = GraphMemory()
        query_engine = GraphQueryEngine(graph_memory, VectorMemory())

        path_result = await query_engine.find_path(
            workspace_id=workspace_id,
            from_entity_id=from_entity,
            to_entity_id=to_entity,
            max_depth=max_depth,
            weight_function=weight_function,
        )

        if not path_result:
            raise HTTPException(
                status_code=404, detail="No path found between entities"
            )

        return {
            "from_entity": from_entity,
            "to_entity": to_entity,
            "weight_function": weight_function,
            "path": {
                "length": path_result.path_length,
                "total_weight": path_result.total_weight,
                "entities": [
                    {
                        "id": entity.id,
                        "name": entity.name,
                        "type": entity.entity_type.value,
                        "properties": entity.properties,
                    }
                    for entity in path_result.path_entities
                ],
                "relationships": [
                    {
                        "id": rel.id,
                        "type": rel.relation_type.value,
                        "source_id": rel.source_id,
                        "target_id": rel.target_id,
                        "weight": rel.weight,
                        "properties": rel.properties,
                    }
                    for rel in path_result.path_relationships
                ],
            },
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error finding path: {str(e)}")


@router.post("/graph/pattern/search")
async def search_pattern(
    pattern_data: dict,
    user: User = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id),
    limit: int = Query(10, ge=1, le=50),
):
    """
    Search for patterns in the knowledge graph.

    Args:
        pattern_data: Pattern specification
        limit: Maximum number of results
    """
    try:
        # Parse pattern data
        entity_types = []
        if "entity_types" in pattern_data:
            for et in pattern_data["entity_types"]:
                try:
                    entity_types.append(EntityType(et))
                except ValueError:
                    raise HTTPException(
                        status_code=400, detail=f"Invalid entity type: {et}"
                    )

        relationship_types = []
        if "relationship_types" in pattern_data:
            for rt in pattern_data["relationship_types"]:
                try:
                    relationship_types.append(RelationType(rt))
                except ValueError:
                    raise HTTPException(
                        status_code=400, detail=f"Invalid relationship type: {rt}"
                    )

        pattern = GraphPattern(
            entity_types=entity_types,
            relationship_types=relationship_types,
            min_depth=pattern_data.get("min_depth", 1),
            max_depth=pattern_data.get("max_depth", 3),
            constraints=pattern_data.get("constraints", {}),
        )

        graph_memory = GraphMemory()
        query_engine = GraphQueryEngine(graph_memory, VectorMemory())

        matches = await query_engine.find_pattern(workspace_id, pattern, limit)

        return {
            "pattern": {
                "entity_types": [et.value for et in pattern.entity_types],
                "relationship_types": [rt.value for rt in pattern.relationship_types],
                "min_depth": pattern.min_depth,
                "max_depth": pattern.max_depth,
                "constraints": pattern.constraints,
            },
            "matches": [
                {
                    "confidence_score": match.confidence_score,
                    "entity_count": len(match.matched_entities),
                    "relationship_count": len(match.matched_relationships),
                    "entities": [
                        {
                            "id": entity.id,
                            "name": entity.name,
                            "type": entity.entity_type.value,
                            "properties": entity.properties,
                        }
                        for entity in match.matched_entities
                    ],
                    "relationships": [
                        {
                            "id": rel.id,
                            "type": rel.relation_type.value,
                            "source_id": rel.source_id,
                            "target_id": rel.target_id,
                            "weight": rel.weight,
                            "properties": rel.properties,
                        }
                        for rel in match.matched_relationships
                    ],
                    "details": match.match_details,
                }
                for match in matches
            ],
            "total_matches": len(matches),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error searching pattern: {str(e)}"
        )


@router.get("/graph/analytics")
async def get_graph_analytics(
    user: User = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id),
):
    """
    Get analytics about the knowledge graph.

    Args:
        workspace_id: Workspace identifier
    """
    try:
        graph_memory = GraphMemory()
        query_engine = GraphQueryEngine(graph_memory, VectorMemory())

        analytics = await query_engine.get_analytics(workspace_id)

        return {
            "workspace_id": workspace_id,
            "analytics": {
                "entity_counts": {
                    et.value: count for et, count in analytics.entity_counts.items()
                },
                "relationship_counts": {
                    rt.value: count
                    for rt, count in analytics.relationship_counts.items()
                },
                "connectivity_metrics": analytics.connectivity_metrics,
                "central_entities": [
                    {"entity_id": entity_id, "centrality_score": score}
                    for entity_id, score in analytics.central_entities
                ],
                "clusters": [
                    {"cluster_id": i, "entity_count": len(cluster), "entities": cluster}
                    for i, cluster in enumerate(analytics.clusters)
                ],
            },
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error getting analytics: {str(e)}"
        )


@router.get("/graph/visualize/d3")
async def get_d3_visualization(
    user: User = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id),
    center_entity: str = Query(...),
    depth: int = Query(2, ge=1, le=5),
    max_entities: int = Query(100, ge=10, le=500),
):
    """
    Get D3.js formatted graph visualization data.

    Args:
        center_entity: Center entity ID
        depth: Maximum depth from center
        max_entities: Maximum number of entities
    """
    try:
        graph_memory = GraphMemory()
        query_engine = GraphQueryEngine(graph_memory, VectorMemory())

        subgraph = await query_engine.get_subgraph(
            workspace_id=workspace_id,
            center_entity_id=center_entity,
            depth=depth,
            max_entities=max_entities,
        )

        if not subgraph:
            raise HTTPException(status_code=404, detail="Subgraph not found")

        d3_data = await query_engine.to_d3_format(subgraph)

        return d3_data

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error generating D3 visualization: {str(e)}"
        )


@router.get("/graph/visualize/cytoscape")
async def get_cytoscape_visualization(
    user: User = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id),
    center_entity: str = Query(...),
    depth: int = Query(2, ge=1, le=5),
    max_entities: int = Query(100, ge=10, le=500),
):
    """
    Get Cytoscape.js formatted graph visualization data.

    Args:
        center_entity: Center entity ID
        depth: Maximum depth from center
        max_entities: Maximum number of entities
    """
    try:
        graph_memory = GraphMemory()
        query_engine = GraphQueryEngine(graph_memory, VectorMemory())

        subgraph = await query_engine.get_subgraph(
            workspace_id=workspace_id,
            center_entity_id=center_entity,
            depth=depth,
            max_entities=max_entities,
        )

        if not subgraph:
            raise HTTPException(status_code=404, detail="Subgraph not found")

        cytoscape_data = await query_engine.to_cytoscape_format(subgraph)

        return cytoscape_data

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating Cytoscape visualization: {str(e)}",
        )


@router.get("/graph/export")
async def export_graph_data(
    user: User = Depends(get_current_user),
    workspace_id: str = Depends(get_workspace_id),
    format: str = Query("json", regex="^(json|csv|graphml)$"),
    include_embeddings: bool = Query(False),
):
    """
    Export graph data in various formats.

    Args:
        format: Export format (json, csv, graphml)
        include_embeddings: Whether to include entity embeddings
    """
    try:
        graph_memory = GraphMemory()

        # Get all data
        entities = await graph_memory.get_all_entities(workspace_id)
        relationships = await graph_memory.get_all_relationships(workspace_id)

        if format == "json":
            export_data = {
                "workspace_id": workspace_id,
                "exported_at": datetime.utcnow().isoformat(),
                "format": "json",
                "data": {
                    "entities": [
                        {
                            "id": entity.id,
                            "name": entity.name,
                            "type": entity.entity_type.value,
                            "properties": entity.properties,
                            "created_at": (
                                entity.created_at.isoformat()
                                if entity.created_at
                                else None
                            ),
                        }
                        for entity in entities
                    ],
                    "relationships": [
                        {
                            "id": rel.id,
                            "type": rel.relation_type.value,
                            "source_id": rel.source_id,
                            "target_id": rel.target_id,
                            "weight": rel.weight,
                            "properties": rel.properties,
                            "created_at": (
                                rel.created_at.isoformat() if rel.created_at else None
                            ),
                        }
                        for rel in relationships
                    ],
                },
            }

        elif format == "csv":
            # CSV format for entities
            import csv
            import io
            from datetime import datetime

            output = io.StringIO()
            writer = csv.writer(output)

            # Write entities
            writer.writerow(["id", "name", "type", "properties", "created_at"])
            for entity in entities:
                writer.writerow(
                    [
                        entity.id,
                        entity.name,
                        entity.entity_type.value,
                        json.dumps(entity.properties),
                        entity.created_at.isoformat() if entity.created_at else "",
                    ]
                )

            # Write relationships
            writer.writerow([])  # Empty row separator
            writer.writerow(
                [
                    "id",
                    "type",
                    "source_id",
                    "target_id",
                    "weight",
                    "properties",
                    "created_at",
                ]
            )
            for rel in relationships:
                writer.writerow(
                    [
                        rel.id,
                        rel.relation_type.value,
                        rel.source_id,
                        rel.target_id,
                        rel.weight or 1.0,
                        json.dumps(rel.properties),
                        rel.created_at.isoformat() if rel.created_at else "",
                    ]
                )

            export_data = {
                "workspace_id": workspace_id,
                "exported_at": datetime.utcnow().isoformat(),
                "format": "csv",
                "data": output.getvalue(),
            }

        elif format == "graphml":
            # GraphML format
            graphml_header = """<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns">
  <key id="label" for="node" attr.name="label" attr.type="string"/>
  <key id="type" for="node" attr.name="type" attr.type="string"/>
  <key id="weight" for="edge" attr.name="weight" attr.type="double"/>
  <graph id="G" edgedefault="undirected">
"""

            graphml_nodes = ""
            graphml_edges = ""

            for entity in entities:
                graphml_nodes += f"""
    <node id="{entity.id}">
      <data key="label">{entity.name}</data>
      <data key="type">{entity.entity_type.value}</data>
    </node>"""

            for rel in relationships:
                graphml_edges += f"""
    <edge source="{rel.source_id}" target="{rel.target_id}">
      <data key="weight">{rel.weight or 1.0}</data>
    </edge>"""

            graphml_footer = """
  </graph>
</graphml>"""

            export_data = {
                "workspace_id": workspace_id,
                "exported_at": datetime.utcnow().isoformat(),
                "format": "graphml",
                "data": graphml_header + graphml_nodes + graphml_edges + graphml_footer,
            }

        else:
            raise HTTPException(status_code=400, detail=f"Unsupported format: {format}")

        return export_data

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error exporting graph data: {str(e)}"
        )
