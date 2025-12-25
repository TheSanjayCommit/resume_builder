import streamlit as st
import google_auth_oauthlib.flow
try:
    from googleapiclient.discovery import build
    GOOGLE_API_CLIENT_AVAILABLE = True
except ImportError:
    build = None
    GOOGLE_API_CLIENT_AVAILABLE = False
import os

# Configuration (Safely loaded from secrets)
CLIENT_CONFIG = {
    "web": {
        "client_id": st.secrets["google_auth"]["client_id"],
        "client_secret": st.secrets["google_auth"]["client_secret"],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris": [st.secrets["google_auth"].get("redirect_uri", "http://localhost:8501")],
    }
}
SCOPES = ['https://www.googleapis.com/auth/userinfo.email', 'openid']

def get_flow():
    """Creates a flow instance to manage the OAuth 2.0 Authorization Grant Flow."""
    flow = google_auth_oauthlib.flow.Flow.from_client_config(
        CLIENT_CONFIG,
        scopes=SCOPES,
        redirect_uri=st.secrets["google_auth"].get("redirect_uri", "http://localhost:8501")
    )
    return flow

def get_auth_url():
    """Generates the authorization URL."""
    flow = get_flow()
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true'
    )
    return authorization_url

def get_user_email(code):
    """Exchanges the authorization code for credentials and returns the user's email."""
    try:
        flow = get_flow()
        flow.fetch_token(code=code)
        credentials = flow.credentials
        
        if not GOOGLE_API_CLIENT_AVAILABLE:
            st.error("Google Sign-In is currently unavailable due to a missing dependency (google-api-python-client).")
            return None

        # Verify and get user info
        service = build('oauth2', 'v2', credentials=credentials)
        user_info = service.userinfo().get().execute()
        return user_info.get('email')
    except Exception as e:
        st.error(f"Authentication Failed: {str(e)}")
        return None
