import logging
import networkx as nx
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class GraphStore:
    """
    Knowledge Graph Manager (Layer 3)
    Handles relationships between entities using NetworkX.
    """
    
    def __init__(self):
        self.memory_root = Path.home() / "HVA_Memory"
        self.graph_path = self.memory_root / "knowledge_graph.json"
        
        self.graph = nx.DiGraph()
        self.load_graph()
        
    def load_graph(self):
        """Load graph from JSON file"""
        if self.graph_path.exists():
            try:
                with open(self.graph_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.graph = nx.node_link_graph(data)
                logger.info(f"Loaded knowledge graph with {self.graph.number_of_nodes()} nodes.")
            except Exception as e:
                logger.error(f"Failed to load graph: {e}")
                self.graph = nx.DiGraph()
        else:
            self.graph = nx.DiGraph()

    def save_graph(self):
        """Save graph to JSON file"""
        try:
            data = nx.node_link_data(self.graph)
            with open(self.graph_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save graph: {e}")

    def add_node(self, node_id: str, node_type: str, attributes: Dict[str, Any] = None):
        """Add a node to the graph"""
        attrs = attributes or {}
        attrs["type"] = node_type
        self.graph.add_node(node_id, **attrs)
        self.save_graph()

    def add_edge(self, source: str, target: str, relation: str):
        """Add a relationship between nodes"""
        self.graph.add_edge(source, target, relation=relation)
        self.save_graph()

    def get_related(self, node_id: str) -> List[Dict[str, Any]]:
        """Get all related nodes"""
        if node_id not in self.graph:
            return []
            
        related = []
        # Outgoing edges
        for neighbor in self.graph.successors(node_id):
            edge_data = self.graph.get_edge_data(node_id, neighbor)
            node_data = self.graph.nodes[neighbor]
            related.append({
                "id": neighbor,
                "type": node_data.get("type"),
                "relation": edge_data.get("relation"),
                "direction": "outgoing"
            })
            
        # Incoming edges
        for predecessor in self.graph.predecessors(node_id):
            edge_data = self.graph.get_edge_data(predecessor, node_id)
            node_data = self.graph.nodes[predecessor]
            related.append({
                "id": predecessor,
                "type": node_data.get("type"),
                "relation": edge_data.get("relation"),
                "direction": "incoming"
            })
            
        return related

# Singleton
_graph_store = None

def get_graph_store():
    global _graph_store
    if _graph_store is None:
        _graph_store = GraphStore()
    return _graph_store
