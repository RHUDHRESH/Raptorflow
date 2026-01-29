"""
Graph compiler for LangGraph workflows with caching and hot reload.
"""

import hashlib
import pickle
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import StateGraph

from checkpointing import create_redis_checkpointer


class GraphCompiler:
    """
    Singleton graph compiler with caching and hot reload capabilities.

    Compiles, caches, and manages LangGraph workflow graphs.
    """

    _instance = None

    def __new__(cls):
        """Singleton pattern implementation."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize the graph compiler."""
        if self._initialized:
            return

        self._compiled_graphs: Dict[str, StateGraph] = {}
        self._graph_metadata: Dict[str, Dict[str, Any]] = {}
        self._graph_sources: Dict[str, str] = {}  # Source file paths
        self._last_modified: Dict[str, datetime] = {}
        self._checkpointer: Optional[BaseCheckpointSaver] = None
        self._cache_ttl = timedelta(hours=1)
        self._initialized = True

    def set_checkpointer(self, checkpointer: BaseCheckpointSaver) -> None:
        """Set the checkpointer for compiled graphs."""
        self._checkpointer = checkpointer

    def _generate_cache_key(
        self, graph_name: str, graph_config: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate cache key for graph."""
        key_data = f"{graph_name}"
        if graph_config:
            key_data += str(sorted(graph_config.items()))
        return hashlib.md5(key_data.encode()).hexdigest()

    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached graph is still valid."""
        if cache_key not in self._last_modified:
            return False

        # Check if cache has expired
        last_modified = self._last_modified[cache_key]
        if datetime.now() - last_modified > self._cache_ttl:
            return False

        # Check if source files have been modified (if we have source info)
        source_file = self._graph_sources.get(cache_key)
        if source_file:
            try:
                import os

                file_mtime = datetime.fromtimestamp(os.path.getmtime(source_file))
                if file_mtime > last_modified:
                    return False
            except (OSError, FileNotFoundError):
                pass

        return True

    def compile_graph(
        self,
        graph: StateGraph,
        graph_name: str,
        graph_config: Optional[Dict[str, Any]] = None,
        force_recompile: bool = False,
    ) -> StateGraph:
        """
        Compile a LangGraph workflow graph.

        Args:
            graph: StateGraph to compile
            graph_name: Name for the graph
            graph_config: Optional configuration for compilation
            force_recompile: Force recompilation even if cached

        Returns:
            Compiled StateGraph
        """
        cache_key = self._generate_cache_key(graph_name, graph_config)

        # Check cache
        if not force_recompile and cache_key in self._compiled_graphs:
            if self._is_cache_valid(cache_key):
                return self._compiled_graphs[cache_key]

        try:
            # Compile the graph
            compiled_graph = self._compile_with_checkpointer(graph)

            # Cache the compiled graph
            self._compiled_graphs[cache_key] = compiled_graph
            self._last_modified[cache_key] = datetime.now()

            # Store metadata
            self._graph_metadata[cache_key] = {
                "name": graph_name,
                "config": graph_config or {},
                "compiled_at": datetime.now().isoformat(),
                "nodes": self._extract_graph_nodes(graph),
                "edges": self._extract_graph_edges(graph),
            }

            return compiled_graph

        except Exception as e:
            raise RuntimeError(f"Failed to compile graph '{graph_name}': {str(e)}")

    def _compile_with_checkpointer(self, graph: StateGraph) -> StateGraph:
        """Compile graph with checkpointer if available."""
        if self._checkpointer:
            return graph.compile(checkpointer=self._checkpointer)
        else:
            return graph.compile()

    def _extract_graph_nodes(self, graph: StateGraph) -> List[str]:
        """Extract node names from graph."""
        try:
            return list(graph.nodes.keys())
        except AttributeError:
            return []

    def _extract_graph_edges(self, graph: StateGraph) -> List[Dict[str, Any]]:
        """Extract edge information from graph."""
        try:
            edges = []
            # This is a simplified extraction - actual implementation would depend on LangGraph internals
            if hasattr(graph, "edges"):
                for edge in graph.edges:
                    edges.append(
                        {
                            "source": getattr(edge, "source", "unknown"),
                            "target": getattr(edge, "target", "unknown"),
                            "condition": getattr(edge, "condition", None),
                        }
                    )
            return edges
        except AttributeError:
            return []

    def get_compiled_graph(
        self, graph_name: str, graph_config: Optional[Dict[str, Any]] = None
    ) -> Optional[StateGraph]:
        """
        Get a compiled graph from cache.

        Args:
            graph_name: Name of the graph
            graph_config: Optional configuration

        Returns:
            Compiled graph if found and valid, None otherwise
        """
        cache_key = self._generate_cache_key(graph_name, graph_config)

        if cache_key in self._compiled_graphs and self._is_cache_valid(cache_key):
            return self._compiled_graphs[cache_key]

        return None

    def reload_graph(
        self, graph_name: str, graph_config: Optional[Dict[str, Any]] = None
    ) -> Optional[StateGraph]:
        """
        Reload a graph from source.

        Args:
            graph_name: Name of the graph to reload
            graph_config: Optional configuration

        Returns:
            Reloaded graph if successful, None otherwise
        """
        cache_key = self._generate_cache_key(graph_name, graph_config)

        # Remove from cache to force recompilation
        if cache_key in self._compiled_graphs:
            del self._compiled_graphs[cache_key]

        # Try to get the graph (this will trigger recompilation)
        return self.get_compiled_graph(graph_name, graph_config)

    def validate_graph(self, graph: StateGraph) -> Dict[str, Any]:
        """
        Validate a graph structure.

        Args:
            graph: StateGraph to validate

        Returns:
            Validation result with issues found
        """
        issues = []
        warnings = []

        try:
            # Check for nodes
            nodes = self._extract_graph_nodes(graph)
            if not nodes:
                issues.append("Graph has no nodes")

            # Check for entry point
            if hasattr(graph, "entry_point"):
                if graph.entry_point not in nodes:
                    issues.append(
                        f"Entry point '{graph.entry_point}' not found in nodes"
                    )
            else:
                warnings.append("No explicit entry point defined")

            # Check for isolated nodes
            connected_nodes = set()
            if hasattr(graph, "edges"):
                for edge in graph.edges:
                    source = getattr(edge, "source", None)
                    target = getattr(edge, "target", None)
                    if source:
                        connected_nodes.add(source)
                    if target:
                        connected_nodes.add(target)

            isolated_nodes = set(nodes) - connected_nodes
            if isolated_nodes:
                warnings.append(f"Isolated nodes found: {list(isolated_nodes)}")

            return {
                "valid": len(issues) == 0,
                "issues": issues,
                "warnings": warnings,
                "node_count": len(nodes),
                "edge_count": len(getattr(graph, "edges", [])),
            }

        except Exception as e:
            return {
                "valid": False,
                "issues": [f"Validation error: {str(e)}"],
                "warnings": [],
                "node_count": 0,
                "edge_count": 0,
            }

    def list_cached_graphs(self) -> List[Dict[str, Any]]:
        """
        List all cached graphs with metadata.

        Returns:
            List of graph information
        """
        graphs = []

        for cache_key, metadata in self._graph_metadata.items():
            last_modified = self._last_modified.get(cache_key)
            is_valid = self._is_cache_valid(cache_key)

            graphs.append(
                {
                    "cache_key": cache_key,
                    "name": metadata.get("name", "unknown"),
                    "compiled_at": metadata.get("compiled_at"),
                    "last_modified": (
                        last_modified.isoformat() if last_modified else None
                    ),
                    "is_valid": is_valid,
                    "node_count": len(metadata.get("nodes", [])),
                    "edge_count": len(metadata.get("edges", [])),
                    "config": metadata.get("config", {}),
                }
            )

        return sorted(graphs, key=lambda x: x.get("compiled_at", ""), reverse=True)

    def clear_cache(self, graph_name: Optional[str] = None) -> int:
        """
        Clear cached graphs.

        Args:
            graph_name: Specific graph to clear, or None for all

        Returns:
            Number of graphs cleared
        """
        cleared = 0

        if graph_name:
            # Clear specific graph
            keys_to_remove = []
            for cache_key, metadata in self._graph_metadata.items():
                if metadata.get("name") == graph_name:
                    keys_to_remove.append(cache_key)

            for key in keys_to_remove:
                if key in self._compiled_graphs:
                    del self._compiled_graphs[key]
                if key in self._graph_metadata:
                    del self._graph_metadata[key]
                if key in self._last_modified:
                    del self._last_modified[key]
                if key in self._graph_sources:
                    del self._graph_sources[key]
                cleared += 1
        else:
            # Clear all graphs
            cleared = len(self._compiled_graphs)
            self._compiled_graphs.clear()
            self._graph_metadata.clear()
            self._last_modified.clear()
            self._graph_sources.clear()

        return cleared

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Cache statistics
        """
        total_graphs = len(self._compiled_graphs)
        valid_graphs = sum(
            1 for key in self._compiled_graphs if self._is_cache_valid(key)
        )

        # Calculate memory usage (approximate)
        total_memory = 0
        for graph in self._compiled_graphs.values():
            try:
                total_memory += len(pickle.dumps(graph))
            except:
                pass

        return {
            "total_graphs": total_graphs,
            "valid_graphs": valid_graphs,
            "invalid_graphs": total_graphs - valid_graphs,
            "cache_hit_rate": (
                (valid_graphs / total_graphs * 100) if total_graphs > 0 else 0
            ),
            "estimated_memory_bytes": total_memory,
            "cache_ttl_hours": self._cache_ttl.total_seconds() / 3600,
            "has_checkpointer": self._checkpointer is not None,
        }


# Global instance
graph_compiler = GraphCompiler()


# Convenience functions
def compile_graph(
    graph: StateGraph,
    name: str,
    config: Optional[Dict[str, Any]] = None,
    force_recompile: bool = False,
) -> StateGraph:
    """
    Compile a graph using the global compiler.

    Args:
        graph: StateGraph to compile
        name: Graph name
        config: Optional configuration
        force_recompile: Force recompilation

    Returns:
        Compiled StateGraph
    """
    return graph_compiler.compile_graph(graph, name, config, force_recompile)


def get_graph(
    name: str, config: Optional[Dict[str, Any]] = None
) -> Optional[StateGraph]:
    """
    Get a compiled graph from cache.

    Args:
        name: Graph name
        config: Optional configuration

    Returns:
        Compiled graph if found
    """
    return graph_compiler.get_compiled_graph(name, config)


def reload_graph(
    name: str, config: Optional[Dict[str, Any]] = None
) -> Optional[StateGraph]:
    """
    Reload a graph from source.

    Args:
        name: Graph name
        config: Optional configuration

    Returns:
        Reloaded graph if successful
    """
    return graph_compiler.reload_graph(name, config)


def list_graphs() -> List[Dict[str, Any]]:
    """List all cached graphs."""
    return graph_compiler.list_cached_graphs()


def clear_cache(name: Optional[str] = None) -> int:
    """Clear cached graphs."""
    return graph_compiler.clear_cache(name)


def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics."""
    return graph_compiler.get_cache_stats()


def initialize_compiler(redis_checkpointer: bool = True) -> None:
    """
    Initialize the global graph compiler.

    Args:
        redis_checkpointer: Whether to use Redis checkpointer
    """
    if redis_checkpointer:
        checkpointer = create_redis_checkpointer()
        graph_compiler.set_checkpointer(checkpointer)
