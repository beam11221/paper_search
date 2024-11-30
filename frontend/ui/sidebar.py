import streamlit as st
from typing import Callable

class Sidebar:
    def __init__(self, status_check_callback: Callable):
        self.status_check_callback = status_check_callback

    def render(self):
        with st.sidebar:
            st.title("🎓 Academic Paper Search")
            st.markdown("---")
            
            mode = st.radio(
                "Select Mode:",
                ["Search Papers", "Add Paper"]
            )
            
            st.markdown("---")
            st.markdown("""
            ### About
            This application allows you to:
            - Search through academic papers using semantic search
            - Add new papers to the database
            - Analyze papers by their similarity
            """)
            
            st.markdown("---")
            st.markdown("### System Status")
            if self.status_check_callback():
                st.success("API: Connected")
            else:
                st.error("API: Not Connected")
        
        return mode