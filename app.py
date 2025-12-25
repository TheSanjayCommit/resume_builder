import streamlit as st
import os

# Set page config
st.set_page_config(
    page_title="AI Resume Builder",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for UI enhancements
st.markdown("""
<style>
    .main {
        padding-top: 2rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
    }
</style>
""", unsafe_allow_html=True)

from utils.resume_data import ResumeBuilder
from utils.ai_engine import AIEngine
from utils.builder_flow import render_builder
from utils.pdf_generator import ResumeGenerator
from utils.auth import get_auth_url, get_user_email
import time

def main():
    st.title("AI Resume Builder & Career Assistant")
    
    # Initialize session state if not already set
    if 'page' not in st.session_state:
        st.session_state.page = 'onboarding'
    
    # Initialize Core Classes
    builder = ResumeBuilder()
    
    # Initialize AI Engine (handle potential errors gracefully)
    try:
        ai_engine = AIEngine()
        st.sidebar.success("AI Engine: Online 🟢")
    except Exception as e:
        st.sidebar.error(f"AI Engine: Offline 🔴 ({str(e)})")
        st.stop()

    # Sidebar Navigation
    st.sidebar.title("Navigation")
    steps = ["Onboarding", "Role Selection", "Resume Builder", "Preview & Export"]
    
    # Simple progress tracking map
    display_page_map = {
        'onboarding': "Onboarding",
        'role_selection': "Role Selection",
        'builder': "Resume Builder",
        'preview': "Preview & Export"
    }
    
    current_step_name = display_page_map.get(st.session_state.page, "Onboarding")
    st.sidebar.markdown(f"**Current Step:** {current_step_name}")
    
 
        
    # --- PAGE: ONBOARDING ---
    if st.session_state.page == 'onboarding':
        st.header("Welcome to your Career Assistant")
        st.write("We'll help you build an ATS-optimized resume in minutes.")
        
        # Check for auth code in URL (Callback handling)
        if "code" in st.query_params:
            with st.spinner("Authenticating..."):
                code = st.query_params["code"]
                user_email = get_user_email(code)
                if user_email:
                    st.session_state.email = user_email
                    st.session_state.page = 'role_selection'
                    # Clear query params to prevent re-auth loops
                    st.query_params.clear()
                    st.rerun()
        
        # Show Sign-In Button if not logged in
        if 'email' not in st.session_state:
            auth_url = get_auth_url()
            st.markdown(f'''
                <a href="{auth_url}" target="_self">
                    <button style="
                        background-color: #4285F4;
                        color: white;
                        padding: 12px 24px;
                        border: none;
                        border-radius: 4px;
                        cursor: pointer;
                        font-size: 16px;
                        font-family: Roboto, sans-serif;
                        width: 100%;
                    ">
                        Sign in with Google
                    </button>
                </a>
            ''', unsafe_allow_html=True)
            
            st.markdown("---")
            st.caption("Or continue as guest (Data might not be saved properly)")
            if st.button("Continue as Guest"):
                st.session_state.email = "guest@example.com"
                st.session_state.page = 'role_selection'
                st.rerun()
    
    # --- PAGE: ROLE SELECTION ---
    elif st.session_state.page == 'role_selection':
        st.header("Step 2: Define Your Goal")
        st.write("Select the role you are targeting to get customized recommendations.")
        
        roles = [
            "Software Engineer", 
            "Full Stack Developer", 
            "Data Analyst", 
            "Machine Learning Engineer", 
            "Cybersecurity Specialist",
            "Defense Technology Specialist",
            "Product Manager",
            "Other"
        ]
        
        selected_role = st.selectbox("Select Target Role:", roles)
        
        if selected_role == "Other":
            custom_role = st.text_input("Please specify your role:")
            if custom_role:
                selected_role = custom_role
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Previous Step"):
                st.session_state.page = 'onboarding'
                st.rerun()
        with col2:
            if st.button("Next: Choose Template"):
                builder.set_user_role(selected_role)
                st.session_state.page = 'template_selection'
                st.rerun()

    # --- PAGE: TEMPLATE SELECTION (Placeholder) ---
    elif st.session_state.page == 'template_selection':
        st.header("Step 3: Choose a Template")
        st.write("Select a layout that fits your style.")
        
        templates = ["Classic Professional", "Modern Clean", "Tech Minimalist"]
        selected_template = st.radio("Available Templates:", templates)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Back to Role Selection"):
                st.session_state.page = 'role_selection'
                st.rerun()
        with col2:
            if st.button("Start Building Resume"):
                st.session_state.selected_template = selected_template
                st.session_state.page = 'builder'
                st.rerun()



    # --- PAGE: BUILDER (Placeholder) ---
    elif st.session_state.page == 'builder':
        render_builder(builder, ai_engine)
        
    # --- PAGE: PREVIEW & EXPORT ---
    elif st.session_state.page == 'preview':
        st.header("Final Preview")
        st.success("Your resume is ready!")
        
        # Generate PDF
        resume_data = builder.get_data()
        pdf_gen = ResumeGenerator(resume_data)
        pdf_bytes = pdf_gen.generate()
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Resume Content Preview")
            st.json(resume_data) # Simple preview for now, or we could render HTML
            
        with col2:
            st.subheader("Actions")
            st.download_button(
                label="📄 Download PDF",
                data=pdf_bytes,
                file_name=f"{st.session_state.get('email', 'resume').split('@')[0]}_resume.pdf",
                mime="application/pdf"
            )
            
            st.warning("Want to make changes?")
            if st.button("Edit Resume"):
                st.session_state.page = 'builder'
                st.session_state.current_section = 0
                st.rerun()
            
            if st.button("Start Over"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()


if __name__ == "__main__":
    main()
