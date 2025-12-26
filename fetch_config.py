import json
import requests
import google.auth
from google.oauth2 import service_account
from google.auth.transport.requests import Request

def get_firebase_config():
    try:
        # Load credentials
        creds = service_account.Credentials.from_service_account_file(
            'firebase_key.json',
            scopes=['https://www.googleapis.com/auth/cloud-platform', 'https://www.googleapis.com/auth/firebase']
        )
        
        # Refresh token
        creds.refresh(Request())
        token = creds.token
        
        project_id = creds.project_id
        print(f"Project ID: {project_id}")
        
        # List Web Apps
        headers = {'Authorization': f'Bearer {token}'}
        list_url = f"https://firebase.googleapis.com/v1beta1/projects/{project_id}/webApps"
        
        response = requests.get(list_url, headers=headers)
        if response.status_code != 200:
            print(f"Error listing apps: {response.text}")
            return

        apps = response.json().get('apps', [])
        if not apps:
            print("No Web Apps found. Creating one...")
            create_url = f"https://firebase.googleapis.com/v1beta1/projects/{project_id}/webApps"
            create_resp = requests.post(create_url, headers=headers, json={"displayName": "Streamlit App"})
            if create_resp.status_code == 200: 
                # Re-fetch list to get the new app
                response = requests.get(list_url, headers=headers)
                apps = response.json().get('apps', [])
            else:
                print(f"Error creating app: {create_resp.text}")
                return

        if not apps:
            print("Failed to find or create web app.")
            return

        # Get Config for the first app
        app_id = apps[0]['name'].split("/")[-1] 
        print(f"Found Web App ID: {app_id}")
        
        config_url = f"https://firebase.googleapis.com/v1beta1/projects/{project_id}/webApps/{app_id}/config"
        config_resp = requests.get(config_url, headers=headers)
        
        if config_resp.status_code == 200:
            config = config_resp.json()
            print("CONFIG_FOUND")
            
            # Write to secrets.toml
            toml_header = "[firebase_web]"
            new_section = f"""
{toml_header}
apiKey = "{config.get('apiKey')}"
authDomain = "{config.get('authDomain')}"
projectId = "{config.get('projectId')}"
storageBucket = "{config.get('storageBucket')}"
messagingSenderId = "{config.get('messagingSenderId')}"
appId = "{config.get('appId')}"
"""
            
            secrets_path = ".streamlit/secrets.toml"
            try:
                # Read existing content
                if requests.os.path.exists(secrets_path):
                    with open(secrets_path, "r") as f:
                        content = f.read()
                else:
                    content = ""
                
                # Check if we need to remove old section
                final_content = content
                if toml_header in content:
                    # Simple heuristic: Split and keep top part
                    parts = content.split(toml_header)
                    final_content = parts[0].strip() + "\n\n"
                
                with open(secrets_path, "w") as f:
                    f.write(final_content + new_section)
                    print(f"Updated {secrets_path} successfully.")
                    
            except Exception as e:
                print(f"Error writing file: {e}")

        else:
            print(f"Error getting config: {config_resp.text}")

    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    get_firebase_config()
