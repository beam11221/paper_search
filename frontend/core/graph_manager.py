import networkx as nx
from pyvis.network import Network
import streamlit.components.v1 as components
from typing import Dict, List
import json
from core.config import GRAPH_OPTIONS, NODE_COLORS, NODE_SIZES, FONT_SIZES

class GraphManager:
    def __init__(self):
        self.graph = nx.Graph()
        self.expanded_nodes = set()
        self.node_details = {}

    def clear(self):
        """Clear all graph data"""
        self.graph.clear()
        self.expanded_nodes.clear()
        self.node_details.clear()

    def add_search_results(self, results: List[Dict]):
        """Process search results and add to graph"""
        for i, paper_details in enumerate(results):
            node_id = paper_details["title"]
            self.node_details[node_id] = paper_details
            self.graph.add_node(node_id)
            
            if i > 0:  # Connect to first node
                self.graph.add_edge(
                    results[0]["title"],
                    node_id,
                    weight=paper_details["similarity"]
                )

    def add_expanded_nodes(self, parent_id: str, results: List[Dict]):
        """Add expanded nodes to the graph"""
        for paper_details in results:
            node_id = paper_details["title"]
            self.node_details[node_id] = paper_details
            self.graph.add_node(node_id)
            self.graph.add_edge(
                parent_id,
                node_id,
                weight=paper_details["similarity"]
            )
        self.expanded_nodes.add(parent_id)

    def visualize(self):
        """Create and display the network visualization"""
        net = Network(height="800px", width="100%", bgcolor="#ffffff", 
                     font_color="black")
        
        # Convert options to JSON string
        net.set_options(json.dumps(GRAPH_OPTIONS))
        
        # Add nodes
        for node in self.graph.nodes():
            details = self.node_details.get(str(node), {})
            
            # Determine node properties
            is_root = len(str(node).split('_')) == 2
            is_expanded = str(node) in self.expanded_nodes
            
            color = (NODE_COLORS["root"] if is_root else 
                    NODE_COLORS["expanded"] if is_expanded else 
                    NODE_COLORS["related"])
            
            size = NODE_SIZES["large"] if (is_root or is_expanded) else NODE_SIZES["small"]
            font_size = FONT_SIZES["large"] if (is_root or is_expanded) else FONT_SIZES["small"]
            
            # Create hover text and wrapped label
            hover_text = (f"Title: {details.get('title', '')}\n\n"
                         f"Abstract: {details.get('abstract', '')}\n\n"
                         f"Link: {details.get('link', '')}")
            
            title = details.get('title', str(node))
            wrapped_title = '\n'.join(
                [title[i:i+30] 
                 for i in range(0, len(title), 30)]
            )
            
            net.add_node(
                str(node),
                label=wrapped_title,
                title=hover_text,
                color=color,
                size=size,
                shape="box",
                font={'size': font_size, 'face': 'arial', 
                      'strokeWidth': 2, 'strokeColor': '#ffffff'},
                margin=10
            )
        
        # Add edges
        for edge in self.graph.edges(data=True):
            width = edge[2].get('weight', 1) * 1.5
            net.add_edge(
                str(edge[0]), 
                str(edge[1]), 
                width=width,
                color={'color': '#848484', 'highlight': '#1B5299'},
                smooth={'type': 'continuous', 'roundness': 0.5}
            )
        
        # Display the graph
        net.save_graph("temp_graph.html")
        with open("temp_graph.html", 'r', encoding='utf-8') as f:
            html_string = f.read()
        components.html(html_string, height=800)