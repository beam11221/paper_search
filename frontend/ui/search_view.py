import streamlit as st
from typing import Callable, List

class SearchView:
    def __init__(self, search_callback: Callable, expand_callback: Callable):
        self.search_callback = search_callback
        self.expand_callback = expand_callback

    def render(self):
        st.header("🔍 Search Papers")
        
        # Initialize session state for the query and limit
        if 'search_query' not in st.session_state:
            st.session_state.search_query = ""
        if 'search_limit' not in st.session_state:
            st.session_state.search_limit = 5

        # Search interface
        query = st.text_input("Enter your search query", key="search_input", 
                            value=st.session_state.search_query)
        col1, col2 = st.columns([2, 1])
        
        with col1:
            search_clicked = st.button("Search")
        with col2:
            limit = st.number_input("Results limit", 
                                  min_value=1, max_value=50, value=st.session_state.search_limit)

        if search_clicked and query:
            st.session_state.search_query = query
            st.session_state.search_limit = limit
            self.search_callback(query, limit)

        return {"query": query, "limit": limit, "search_clicked": search_clicked}

    def render_expansion_controls(self, unexpanded_nodes: List[str]):
        # Initialize session state for selected node
        if 'selected_node' not in st.session_state:
            st.session_state.selected_node = None

        # Only show controls if there are unexpanded nodes
        if unexpanded_nodes:
            container = st.container()
            with container:
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    node_to_expand = st.selectbox(
                        "Select node to expand:",
                        unexpanded_nodes,
                        key="node_select"
                    )
                    st.session_state.selected_node = node_to_expand
                
                with col2:
                    expand_clicked = st.button("Expand", key="expand_button")
                    
                if expand_clicked and st.session_state.selected_node:
                    self.expand_callback(st.session_state.selected_node)

            return {"node": node_to_expand, "expand_clicked": expand_clicked}
        return None