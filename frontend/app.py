import streamlit as st
from typing import Dict, List
import networkx as nx

from api.api_client import PaperAPIClient
from ui.sidebar import Sidebar
from ui.components import PaperSubmissionForm
from utils.visualization import NetworkVisualizer

# Initialize session state
if 'graph' not in st.session_state:
    st.session_state.graph = nx.Graph()
if 'expanded_nodes' not in st.session_state:
    st.session_state.expanded_nodes = set()
if 'node_details' not in st.session_state:
    st.session_state.node_details = {}


class PaperSearchApp:
    def __init__(self):
        st.set_page_config(
            page_title="Academic Paper Search",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        self.api_client = PaperAPIClient()
        self.sidebar = Sidebar(self.api_client.check_api_status)
        self.paper_submission = PaperSubmissionForm(self.api_client)
        self.network_graph = NetworkVisualizer()

    def preprocess_search_result(self, search_results: List[Dict[str, str]]):
        nodes = []
        for i, paper_details in enumerate(search_results):
            node_id = paper_details["title"]

            nodes.append({
                "id": node_id,
                "label": f"Doc {i}",
                "details": paper_details
            })
            st.session_state.node_details[node_id] = paper_details

        edges = [
            {"from": node_id, "to": paper_details["title"], 
            "weight": paper_details["similarity"]} 
            for paper_details in search_results
        ]

        return {"nodes": nodes, "edges": edges}

    def get_expanded_nodes(self, node_id):
        """Generate related nodes with detailed information"""
        search_results = self.api_client.search_papers(node_id, limit=5)
        nodes = []

        for i, paper_details in enumerate(search_results):
            new_id = paper_details["title"]
            nodes.append({
                "id": node_id,
                "label": f"Related {i}",
                "details": paper_details
            })
            st.session_state.node_details[new_id] = paper_details

        edges = [
            {"from": node_id, "to": paper_details["title"],
            "weight": paper_details["similarity"]} 
            for paper_details in search_results
        ]

        return {"nodes": nodes, "edges": edges}

    def render_paper_search(self):
        """Render paper search interface"""
        st.header("🔍 Search Papers")
        
        # Initialize session state
        if 'graph_history' not in st.session_state:
            st.session_state.graph_history = []
        
        # Search form
        query = st.text_input("Enter your search query")
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            search_button = st.button("Search")
        with col2:
            limit = st.number_input("Results limit", min_value=1, max_value=50, value=5)

        if search_button and query:
            st.session_state.graph.clear()
            st.session_state.expanded_nodes.clear()
            st.session_state.node_details.clear()

            results = self.api_client.search_papers(query, limit)
            results = self.preprocess_search_result(results)
            
            # Add to graph
            for node in results["nodes"]:
                st.session_state.graph.add_node(node["id"])
            for edge in results["edges"]:
                st.session_state.graph.add_edge(
                    edge["from"], 
                    edge["to"], 
                    weight=edge["weight"]
                )

         # Show expand options if graph has nodes
        if st.session_state.graph.nodes:
            unexpanded = [node for node in st.session_state.graph.nodes() 
                        if node not in st.session_state.expanded_nodes]
            
            if unexpanded:
                col1, col2 = st.columns([3, 1])
                with col1:
                    node_to_expand = st.selectbox(
                        "Select node to expand:",
                        unexpanded
                    )
                with col2:
                    if st.button("Expand"):
                        expansion = self.get_expanded_nodes(node_to_expand)
                        
                        # Add new nodes and edges
                        for node in expansion["nodes"]:
                            st.session_state.graph.add_node(node["id"])
                        for edge in expansion["edges"]:
                            st.session_state.graph.add_edge(
                                edge["from"], 
                                edge["to"],
                                weight=edge["weight"]
                            )
                        
                        st.session_state.expanded_nodes.add(node_to_expand)

        self.network_graph.create_network()

    def main(self):
        """Main application logic"""
        mode = self.sidebar.render()
        
        if mode == "Search Papers":
            self.render_paper_search()
        elif mode == "Add Paper":
            self.paper_submission.render()
        else:
            pass

if __name__ == "__main__":
    app = PaperSearchApp()
    app.main()