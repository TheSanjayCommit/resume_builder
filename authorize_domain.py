import json
import requests
import google.auth
from google.oauth2 import service_account
from google.auth.transport.requests import Request
import sys

def authorize_domain():
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

        headers = {
            'Authorization': f'Bearer {token}', 
            'Content-Type': 'application/json'
        }
        
        url = f"https://identitytoolkit.googleapis.com/admin/v2/projects/{project_id}/config"
        
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Error fetching config: {response.text}")
            return

        config = response.json()
        authorized_domains = config.get('authorizedDomains', [])
        
        print("--- CURRENT AUTHORIZED DOMAINS ---")
        for d in authorized_domains:
            print(d)
        print("----------------------------------")

        # Domains to ensure are present
        domains_to_add = ["localhost", "127.0.0.1"]
        
        # Check if CLI arg provided
        if len(sys.argv) > 1:
            custom_domain = sys.argv[1]
            if "://" in custom_domain:
                custom_domain = custom_domain.split("://")[1]
            if custom_domain.endswith("/"):
                custom_domain = custom_domain[:-1]
            domains_to_add.append(custom_domain)

        updated = False
        for d in domains_to_add:
            if d not in authorized_domains:
                authorized_domains.append(d)
                updated = True
                print(f"Adding: {d}")
        
        if updated:
            update_url = f"{url}?updateMask=authorizedDomains"
            body = {"authorizedDomains": authorized_domains}
            
            update_resp = requests.patch(update_url, headers=headers, json=body)
            if update_resp.status_code == 200:
                print("SUCCESS: Domains updated.")
            else:
                print(f"Error updating config: {update_resp.text}")
        else:
            print("All requested domains are already authorized.")

    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    authorize_domain()
