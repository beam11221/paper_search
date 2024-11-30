import streamlit as st
from typing import Callable

class SubmissionView:
    def __init__(self, submit_callback: Callable):
        self.submit_callback = submit_callback

    def render(self):
        st.header("📝 Add New Paper")
        
        with st.form("paper_submission"):
            title = st.text_input("Paper Title")
            abstract = st.text_area("Abstract", height=200)
            submitted = st.form_submit_button("Submit Paper")
            
            if submitted and title and abstract:
                with st.spinner("Adding paper..."):
                    result = self.submit_callback(title, abstract)
                    if result:
                        st.success(f"Paper added successfully! ID: {result['paper_id']}")
                        st.balloons()

            return {"title": title, "abstract": abstract, "submitted": submitted}