import streamlit as st
# from utils.visualization import NetworkVisualizer

class PaperSubmissionForm:
    def __init__(self, api_client):
        self.api_client = api_client

    def render(self):
        st.header("📝 Add New Paper")
        
        with st.form("paper_submission"):
            title = st.text_input("Paper Title")
            abstract = st.text_area("Abstract", height=200)
            submitted = st.form_submit_button("Submit Paper")
            
            if submitted and title and abstract:
                with st.spinner("Adding paper..."):
                    result = self.api_client.add_paper(title, abstract)
                    if result:
                        st.success(f"Paper added successfully! ID: {result['paper_id']}")
                        st.balloons()

# class PaperSearchInterface:
#     def __init__(self, api_client, graph_manager):
#         self.api_client = api_client
#         self.graph_manager = graph_manager
#         self.visualizer = NetworkVisualizer()

#     def render(self):
#         st.header("🔍 Search Papers")
        
#         # Search form and visualization implementation
#         # ... (Previous search implementation moved here)