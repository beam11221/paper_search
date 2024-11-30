from pyvis.network import Network
import streamlit.components.v1 as components
import streamlit as st
import json
from core.config import GRAPH_OPTIONS

class NetworkVisualizer:
    def __init__(self):
        pass

    def create_network(self):
        net = Network(height="800px", width="100%", bgcolor="#ffffff", font_color="black")
        net.set_options(json.dumps(GRAPH_OPTIONS))
        
        ## Add nodes with hover details
        for node in st.session_state.graph.nodes():
            details = st.session_state.node_details.get(str(node), {})
            
            # Node size and color logic
            if len(str(node).split('_')) == 2:  # Root nodes
                size = 35
                color = "#4299e1"  # Blue
                font_size = 16
                shape = "box"
            elif str(node) in st.session_state.expanded_nodes:  # Expanded nodes
                size = 35
                color = "#48bb78"  # Green
                font_size = 16
                shape = "box"
            else:  # Related nodes
                size = 25
                color = "#a0aec0"  # Gray
                font_size = 12
                shape = "box"
                
            hover_text = f"Title: {details["title"]}\n\nAbstract: {details["abstract"]}\n\nLink: {details["link"]}"
            
            # Calculate label width and wrap text
            title = details.get('title', str(node))
            wrapped_title = '\n'.join([title[i:i+30] for i in range(0, len(title), 30)])
            
            net.add_node(
                str(node),
                label=wrapped_title,
                title=hover_text,
                color=color,
                size=size,
                shape=shape,
                font={'size': font_size, 'face': 'arial', 'strokeWidth': 2, 'strokeColor': '#ffffff'},
                margin=10
            )
        
        # Add edges with weight-based width
        for edge in st.session_state.graph.edges(data=True):
            width = edge[2].get('weight', 1) * 1.5  # Slightly thinner edges
            net.add_edge(str(edge[0]), str(edge[1]), 
                        width=width,
                        color={'color': '#848484', 'highlight': '#1B5299'},
                        smooth={'type': 'continuous', 'roundness': 0.5})
        
        # Save and display the graph
        self.display(net)
        
        return net

    def display(self, net):
        net.save_graph("temp_graph.html")
        with open("temp_graph.html", 'r', encoding='utf-8') as f:
            html_string = f.read()
        components.html(html_string, height=800)