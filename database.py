# python
from typing import List, Dict, Any, Optional
import logging
import networkx as nx
from config import settings

logger = logging.getLogger(__name__)


class Neo4jDatabase:
    """
    In-memory graph-backed replacement for the original Neo4j database layer.
    Uses NetworkX to model classes, methods, and relationships so the rest of
    the application can run without the 'neo4j' package or a Neo4j server.
    """

    def __init__(self):
        # Directed multigraph to allow multiple edge types (HAS_METHOD, DEPENDS_ON)
        self.graph = nx.MultiDiGraph()
        # Index for quick class lookup by (name, package) and by name
        self._class_key_index: Dict[str, str] = {}          # key -> node_id
        self._class_name_index: Dict[str, List[str]] = {}   # name -> [node_ids]
        logger.info("Initialized in-memory graph database (NetworkX backend)")

    def _class_node_id(self, name: str, package: str) -> str:
        # Unique identifier for a class node
        return f"class::{package}.{name}" if package else f"class::{name}"

    def _method_node_id(self, class_name: str, method_name: str) -> str:
        # Unique identifier for a method node
        return f"method::{class_name}::{method_name}"

    def close(self):
        # No external resources to close in the in-memory implementation
        pass

    def execute_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict]:
        """
        Compatibility layer for code paths that expect Cypher queries.
        - Ignores CREATE INDEX statements (no-op).
        - Recognizes the specific stats query used by get_status and returns counts.
        """
        if not isinstance(query, str):
            return []

        q = " ".join(query.split()).strip().lower()

        # Ignore index creation statements (no-op)
        if q.startswith("create index"):
            logger.debug(f"Ignoring index creation query in in-memory DB: {query}")
            return []

        # Handle the specific stats query used in JavaDevelopmentAgent.get_status
        if "match (c:class)" in q and "return count(distinct c) as classes" in q:
            classes = sum(1 for _, data in self.graph.nodes(data=True) if data.get("label") == "Class")
            methods = sum(
                1 for u, v, k, data in self.graph.edges(keys=True, data=True)
                if data.get("type") == "HAS_METHOD"
            )
            return [{"classes": classes, "methods": methods}]

        # Any other ad-hoc query is not supported in the in-memory backend
        logger.debug(f"Unsupported execute_query in in-memory DB, query ignored: {query}")
        return []

    def create_indexes(self):
        # No indexes needed for in-memory graph, but keep method for compatibility
        logger.info("create_indexes: no-op for in-memory database")

    def create_class_node(self, class_info: Dict[str, Any]) -> bool:
        """
        Create or update a class node.
        Expected keys in class_info: name, package, modifiers, extends, implements,
        file_path, line_number, documentation
        """
        try:
            name = class_info.get("name", "")
            package = class_info.get("package", "")
            node_id = self._class_node_id(name, package)

            # Upsert node
            self.graph.add_node(
                node_id,
                label="Class",
                name=name,
                package=package,
                modifiers=class_info.get("modifiers"),
                extends=class_info.get("extends"),
                implements=class_info.get("implements"),
                file_path=class_info.get("file_path"),
                line_number=class_info.get("line_number"),
                documentation=class_info.get("documentation"),
            )

            # Update indices
            key = f"{package}::{name}"
            self._class_key_index[key] = node_id
            self._class_name_index.setdefault(name, [])
            if node_id not in self._class_name_index[name]:
                self._class_name_index[name].append(node_id)

            return True
        except Exception as e:
            logger.error(f"Error creating class node: {e}")
            return False

    def create_method_node(self, method_info: Dict[str, Any]) -> bool:
        """
        Create or update a method node and link it to its class via HAS_METHOD.
        Expected keys in method_info: class_name, package, method_name, return_type,
        parameters, modifiers, line_number, documentation, body
        """
        try:
            class_name = method_info.get("class_name", "")
            package = method_info.get("package", "")
            method_name = method_info.get("method_name", "")

            class_node_id = self._class_node_id(class_name, package)
            if class_node_id not in self.graph:
                logger.warning(f"Class node not found for method: {class_name} (package: {package})")
                return False

            method_node_id = self._method_node_id(class_name, method_name)
            self.graph.add_node(
                method_node_id,
                label="Method",
                name=method_name,
                class_name=class_name,
                return_type=method_info.get("return_type"),
                parameters=method_info.get("parameters"),
                modifiers=method_info.get("modifiers"),
                line_number=method_info.get("line_number"),
                documentation=method_info.get("documentation"),
                body=method_info.get("body"),
            )

            # Link class -> method
            self.graph.add_edge(class_node_id, method_node_id, type="HAS_METHOD")
            return True
        except Exception as e:
            logger.error(f"Error creating method node: {e}")
            return False

    def create_dependency_relationship(
        self,
        from_class: str,
        to_class: str,
        dependency_type: str,
        package_from: str = "",
        package_to: str = "",
    ) -> bool:
        """
        Create a DEPENDS_ON relationship between two class nodes.
        """
        try:
            c1 = self._class_node_id(from_class, package_from)
            c2 = self._class_node_id(to_class, package_to)

            if c1 not in self.graph or c2 not in self.graph:
                logger.warning(f"Cannot create dependency, missing nodes: {c1} or {c2}")
                return False

            self.graph.add_edge(c1, c2, type="DEPENDS_ON", dependency_type=dependency_type)
            return True
        except Exception as e:
            logger.error(f"Error creating dependency relationship: {e}")
            return False

    def find_related_classes(self, class_name: str, max_depth: int = 2) -> List[Dict]:
        """
        Find classes related to the given class within specified depth.
        Uses DEPENDS_ON relationships between Class nodes.
        """
        try:
            # Collect all class node ids matching the given name
            candidates = self._class_name_index.get(class_name, [])
            if not candidates:
                return []

            results: Dict[str, Dict[str, Any]] = {}
            # Undirected view for "either direction" traversal
            ug = self.graph.to_undirected()

            for start_id in candidates:
                # BFS up to max_depth
                lengths = nx.single_source_shortest_path_length(ug, start_id, cutoff=max_depth)
                for node_id, dist in lengths.items():
                    if node_id == start_id:
                        continue
                    node_data = self.graph.nodes[node_id]
                    if node_data.get("label") != "Class":
                        continue
                    key = node_id
                    if key not in results or dist < results[key]["distance"]:
                        results[key] = {
                            "name": node_data.get("name"),
                            "package": node_data.get("package"),
                            "distance": dist,
                        }

            # Sort by distance then name
            sorted_items = sorted(results.values(), key=lambda r: (r["distance"], r["name"] or ""))
            return sorted_items
        except Exception as e:
            logger.error(f"Error finding related classes: {e}")
            return []

    def get_class_methods(self, class_name: str, package: str = "") -> List[Dict]:
        """
        Get all methods of a specific class by traversing HAS_METHOD edges.
        """
        try:
            class_node_id = self._class_node_id(class_name, package)
            if class_node_id not in self.graph:
                return []

            methods: List[Dict] = []
            for _, method_node_id, data in self.graph.out_edges(class_node_id, data=True):
                if data.get("type") != "HAS_METHOD":
                    continue
                node_data = self.graph.nodes[method_node_id]
                if node_data.get("label") != "Method":
                    continue
                methods.append({
                    "method_name": node_data.get("name"),
                    "return_type": node_data.get("return_type"),
                    "parameters": node_data.get("parameters"),
                    "modifiers": node_data.get("modifiers"),
                    "documentation": node_data.get("documentation"),
                })

            # Order by method name to mimic the Cypher ORDER BY m.name
            methods.sort(key=lambda m: m.get("method_name") or "")
            return methods
        except Exception as e:
            logger.error(f"Error getting class methods: {e}")
            return []


# Global database instance
db = Neo4jDatabase()