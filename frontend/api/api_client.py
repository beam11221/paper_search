import requests
from typing import Dict, List
import streamlit as st

from core.config import API_URL

class PaperAPIClient:
    def __init__(self):
        self.api_url = API_URL

    def add_paper(self, title: str, abstract: str) -> Dict:
        """Send paper to backend API"""
        try:
            response = requests.post(
                f"{self.api_url}/add_paper",
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
                f"{self.api_url}/query",
                json={"query_text": query, "top_k": limit}
            )
            return response.json()["results"]
        except requests.exceptions.RequestException as e:
            st.error(f"Error searching papers: {str(e)}")
            return []

    def check_api_status(self) -> bool:
        """Check if API is accessible"""
        try:
            response = requests.get(f"{self.api_url}/docs")
            return response.status_code == 200
        except:
            return False