import streamlit as st
import requests
import json
import time
from typing import Dict, List
import plotly.io as pio
import pandas as pd
from typing import Dict, List


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
        
        # Search form
        query = st.text_input("Enter your search query")
        # col1, col2 = st.columns([3, 1])
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            search_button = st.button("Search")
        with col2:
            limit = st.number_input("Results limit", min_value=1, max_value=50, value=10)
        with col3:
            show_graph = st.checkbox("Show Graph", value=False)

        if search_button and query:
            with st.spinner("Searching..."):
                results = self.search_papers(query, limit)
                
                if results:
                    # Show the result
                    st.subheader(f"Found {len(results)} results")
                    for i, paper in enumerate(results, 1):
                        with st.expander(f"{i}. {paper['title']} (Score: {paper['similarity']:.2f})"):
                            st.markdown(f"**Abstract:**\n{paper['abstract']}")
                            st.markdown(f"**Link:**\n{paper['link']}")
                            st.markdown(f"**Paper ID:** `{paper['paper_id']}`")
                    # Show graph

                else:
                    st.info("No results found")
    
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
        st.markdown("---")
        st.markdown("*Built with Streamlit, FastAPI & OpenAI*")

if __name__ == "__main__":
    app = PaperSearchApp()
    app.main()