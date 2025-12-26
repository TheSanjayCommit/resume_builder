import streamlit as st
import firebase_admin
from firebase_admin import credentials, auth
import os
import json

# Initialize Firebase Admin SDK
# Use the local file if available, otherwise try to load from Streamlit secrets
if not firebase_admin._apps:
    try:
        cred = None
        if os.path.exists('firebase_key.json'):
            cred = credentials.Certificate('firebase_key.json')
        elif "firebase" in st.secrets:
            # secrets["firebase"] might be a dict or a string?
            # Streamlit secrets usually parses TOML into dicts.
            key_data = dict(st.secrets["firebase"])
            # The private_key in TOML might have \n escaped or literal newlines.
            # Usually Streamlit handles TOML strings correctly.
            cred = credentials.Certificate(key_data)

        if cred:
            firebase_admin.initialize_app(cred)
            print("Firebase Admin Initialized")
        else:
            # Only error if we really need it initialized now? 
            # Ideally we warn but don't crash unless using admin features.
            pass 
    except Exception as e:
        st.error(f"Failed to initialize Firebase: {e}")

def verify_token(id_token):
    """Verifies a Firebase ID token and returns the decoded token dict."""
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except Exception as e:
        print(f"Token verification failed: {e}")
        return None

def get_login_ui():
    """Returns the HTML/JS for the client-side Firebase Login."""
    
    # Attempt to get config from secrets
    try:
        web_config = st.secrets.get("firebase_web", {})
        if not web_config:
             return """
             <div style="padding: 20px; border: 1px solid #f44336; border-radius: 5px; color: #f44336;">
                <strong>Configuration Missing/Loading...</strong><br>
                Please wait for auto-configuration to complete or check secrets.toml.
             </div>
             """
             
        api_key = web_config.get("apiKey", "")
        auth_domain = web_config.get("authDomain", "")
        project_id = web_config.get("projectId", "")
        storage_bucket = web_config.get("storageBucket", "")
        messaging_sender_id = web_config.get("messagingSenderId", "")
        app_id = web_config.get("appId", "")

    except Exception:
        return "<div>Error loading configuration</div>"

    html = f"""
    <script type="module">
      import {{ initializeApp }} from "https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js";
      import {{ getAuth, GoogleAuthProvider, signInWithPopup }} from "https://www.gstatic.com/firebasejs/10.7.1/firebase-auth.js";

      const firebaseConfig = {{
        apiKey: "{api_key}",
        authDomain: "{auth_domain}",
        projectId: "{project_id}",
        storageBucket: "{storage_bucket}",
        messagingSenderId: "{messaging_sender_id}",
        appId: "{app_id}"
      }};

      // Initialize Firebase
      const app = initializeApp(firebaseConfig);
      const auth = getAuth(app);
      const provider = new GoogleAuthProvider();

      async function signIn() {{
          try {{
              const result = await signInWithPopup(auth, provider);
              const credential = GoogleAuthProvider.credentialFromResult(result);
              const token = credential.accessToken;
              const user = result.user;
              const idToken = await user.getIdToken();
              
              // Pass token to Streamlit via URL query param reloading
              window.parent.location.href = window.parent.location.pathname + '?firebase_token=' + idToken;
              
          }} catch (error) {{
              console.error(error);
              if (error.code === 'auth/unauthorized-domain') {{
                  alert("Login Failed: Unauthorized Domain.\\n\\nFirebase sees origin: " + window.origin + "\\nHref: " + window.location.href + "\\n\\nThe app must be run on an authorized domain (localhost).");
              }} else {{
                  alert("Login Failed: " + error.message);
              }}
          }}
      }}
      
      window.signIn = signIn;
    </script>

    <button onclick="signIn()" style="
        background-color: #4285F4;
        color: white;
        padding: 12px 24px;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-size: 16px;
        font-family: Roboto, sans-serif;
        width: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
    ">
        <img src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg" width="18" height="18">
        Sign in with Google
    </button>
    """
    return html
