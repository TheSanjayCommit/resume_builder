import streamlit as st
from typing import Dict, Any

class ResumeBuilder:
    def __init__(self):
        if 'resume_data' not in st.session_state:
            st.session_state.resume_data = {
                "contact_info": {},
                "summary": "",
                "skills": [],
                "experience": [],
                "projects": [],
                "education": [],
                "certifications": []
            }
        
        if 'user_role' not in st.session_state:
            st.session_state.user_role = ""
            
        if 'selected_template' not in st.session_state:
            st.session_state.selected_template = "Classic"

    def set_user_role(self, role: str):
        st.session_state.user_role = role

    def update_section(self, section: str, data: Any):
        if section in st.session_state.resume_data:
            st.session_state.resume_data[section] = data

    def get_data(self) -> Dict[str, Any]:
        return st.session_state.resume_data

    def get_role(self) -> str:
        return st.session_state.user_role
