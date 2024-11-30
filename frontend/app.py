import streamlit as st
import requests
import json
import time
from typing import Dict, List
import plotly.io as pio
import pandas as pd
from typing import Dict, List
from streamlit_plotly_events import plotly_events
import plotly.graph_objects as go

# Initialize session state
if 'graph' not in st.session_state:
    st.session_state.graph = nx.Graph()
if 'expanded_nodes' not in st.session_state:
    st.session_state.expanded_nodes = set()
if 'node_details' not in st.session_state:
    st.session_state.node_details = {}


class PaperSearchApp:
    def __init__(self):
        self.API_URL = "http://localhost:7890"
        st.set_page_config(
            page_title="Academic Paper Search",
            layout="wide",
            initial_sidebar_state="expanded"
        )

    def add_paper(self, title: str, abstract: str) -> Dict:
        """Send paper to backend API"""
        try:
            response = requests.post(
                f"{self.API_URL}/add_paper",
                json={"title": title, "abstract": abstract}
            )
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Error adding paper: {str(e)}")
            return None

    def search_papers(self, query: str, limit: int = 10) -> List[Dict]:
        """Search papers using backend API"""
        try:
            response = requests.post(
                f"{self.API_URL}/query",
                json={"query_text": query, "top_k": limit}
            )
            return response.json()["results"]
        except requests.exceptions.RequestException as e:
            st.error(f"Error searching papers: {str(e)}")
            return []

    def render_paper_submission(self):
        """Render paper submission form"""
        st.header("📝 Add New Paper")
        
        with st.form("paper_submission"):
            title = st.text_input("Paper Title")
            abstract = st.text_area("Abstract", height=200)
            submitted = st.form_submit_button("Submit Paper")
            
            if submitted and title and abstract:
                with st.spinner("Adding paper..."):
                    result = self.add_paper(title, abstract)
                    if result:
                        st.success(f"Paper added successfully! ID: {result['paper_id']}")
                        st.balloons()

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
            limit = st.number_input("Results limit", min_value=1, max_value=50, value=10)
        with col3:
            show_graph = st.checkbox("Show Graph", value=False)

        if search_button and query:
            if show_graph:
                with st.spinner("Searching and generating graph..."):
                    response = requests.post(
                        f"{self.API_URL}/search_graph",
                        json={"query_text": query, "top_k": limit}
                    )
                    data = response.json()
                    results = response.json()

                    st.session_state.graph_history = [data]
                    self.display_interactive_graph()
            else:
                results = self.search_papers(query, limit)
                self.display_search_results(results)

        # Display results
        # for i, paper in enumerate(results, 1):
        #     with st.expander(f"{i}. {paper['title']}"):
        #         if 'abstract' in paper:
        #             st.markdown(f"**Abstract:**\n{paper['abstract']}")
        #         st.markdown(f"**Paper ID:** `{paper['paper_id']}`")
        #         st.markdown(f"**link:** `{paper['link']}`")

    
    def display_interactive_graph(self):
        """Display the interactive graph with controls"""
        if not st.session_state.graph_history:
            return

        # Initialize click state if not exists
        if 'last_clicked' not in st.session_state:
            st.session_state.last_clicked = None

        current_graph = st.session_state.graph_history[-1]
        
        # Create main container
        with st.container():
            # Stats and Controls in a fixed header
            header = st.container()
            with header:
                st.subheader("Interactive Paper Network")
                col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
                with col1:
                    st.metric("Papers", current_graph["node_count"])
                with col2:
                    st.metric("Connections", current_graph["edge_count"])
                with col3:
                    if len(st.session_state.graph_history) > 1:
                        if st.button("← Back", key="back_button"):
                            st.session_state.graph_history.pop()
                            st.session_state.last_clicked = None  # Reset click state
                with col4:
                    if st.button("Reset", key="reset_button"):
                        st.session_state.graph_history = []
                        st.session_state.last_clicked = None  # Reset click state

            # Graph container with fixed height
            graph_container = st.container()
            with graph_container:
                fig = go.Figure(data=current_graph["graph_data"]["data"], 
                            layout=current_graph["graph_data"]["layout"])
                
                # Use a stable key for the graph
                clicked_point = plotly_events(
                    fig,
                    click_event=True,
                    override_height=500,
                    key="graph_viewer"  # Static key instead of dynamic
                )

            # Handle click events only when there's a new click
            # if clicked_point and str(clicked_point) != str(st.session_state.last_clicked):
            #     st.session_state.last_clicked = clicked_point  # Update click state
            #     point_index = clicked_point[0]['pointIndex']
            #     paper_id = current_graph["results"][point_index]["paper_id"]
                
            #     with st.spinner("Loading related papers..."):
            #         response = requests.post(
            #             f"{self.API_URL}/expand_graph",
            #             json={"paper_id": paper_id, "limit": 10}
            #         )
            #         if response.ok:
            #             new_graph = response.json()
            #             st.session_state.graph_history.append(new_graph)
            #             st.experimental_rerun()  # Only rerun when we actually have new data

    def display_search_results(self, results: List[Dict]):
        """Display search results in list format"""
        st.subheader(f"Found {len(results)} results")
        for i, paper in enumerate(results, 1):
            with st.expander(f"{i}. {paper['title']}"):
                if 'abstract' in paper:
                    st.markdown(f"**Abstract:**\n{paper['abstract']}")
                st.markdown(f"**Paper ID:** `{paper['paper_id']}`")
                if 'link' in paper:
                    st.markdown(f"**Link:** [{paper['link']}]({paper['link']})")

    def expand_graph(self, paper_id: str, limit: int):
        """Helper function to expand graph from a paper"""
        response = requests.post(
            f"{self.API_URL}/expand_graph",
            json={"paper_id": paper_id, "limit": limit}
        )
        if response.ok:
            new_graph = response.json()
            st.session_state.graph_history.append(new_graph)



    def get_vector_graph(self):
        """Get vector relationship graph from backend API"""
        try:
            response = requests.post(f"{self.API_URL}/vector_graph")
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"Error generating vector graph: {str(e)}")
            return None
        
    def render_vector_graph(self):
        """Render vector relationship graph page"""
        st.header("🕸️ Paper Vector Relationships")
        
        if st.button("Generate Vector Graph", type="primary"):
            with st.spinner("Generating vector relationship graph..."):
                graph_data = self.get_vector_graph()
                
                if graph_data:
                    # Display graph statistics
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Number of Papers", graph_data["node_count"])
                    with col2:
                        st.metric("Number of Connections", graph_data["edge_count"])
                    
                    # Display interactive graph
                    st.plotly_chart(
                        graph_data["graph_data"],
                        use_container_width=True,
                        height=800
                    )
                    
                    st.info("""
                    This graph shows the relationships between papers based on their vector similarity.
                    - Each node represents a paper
                    - Connections indicate semantic similarity
                    - Hover over nodes to see paper details
                    """)

    def render_sidebar(self):
        """Render sidebar with navigation"""
        with st.sidebar:
            st.title("🎓 Academic Paper Search")
            st.markdown("---")
            mode = st.radio(
                "Select Mode:",
                ["Search Papers", "Add Paper", "Vector Graph"]
            )
            
            st.markdown("---")
            st.markdown("""
            ### About
            This application allows you to:
            - Search through academic papers using semantic search
            - Add new papers to the database
            - Analyze papers by their similarity
            """)
            
            # Add system status indicators
            st.markdown("---")
            st.markdown("### System Status")
            try:
                response = requests.get(f"{self.API_URL}/docs")
                if response.status_code == 200:
                    st.success("API: Connected")
                else:
                    st.error("API: Not Connected")
            except:
                st.error("API: Not Connected")
        
        return mode

    def main(self):
        """Main application logic"""
        mode = self.render_sidebar()
        
        if mode == "Search Papers":
            self.render_paper_search()
        elif mode == "Add Paper":
            self.render_paper_submission()
        elif mode == "Vector Graph":
            self.render_vector_graph()
        else:
            pass
        
        # Footer
        # st.markdown("---")
        # st.markdown("*Built with Streamlit, FastAPI & OpenAI*")

if __name__ == "__main__":
    app = PaperSearchApp()
    app.main()