import json
import os

def generate_secrets():
    output = []
    
    # 1. Process Service Account Key (firebase_key.json)
    if os.path.exists('firebase_key.json'):
        try:
            with open('firebase_key.json', 'r') as f:
                key_data = json.load(f)
            
            output.append("[firebase]")
            for k, v in key_data.items():
                if k == "private_key":
                    # Clean up private key newlines for TOML
                    v_sanitized = v.replace('\n', '\\n') 
                    output.append(f'{k} = "{v_sanitized}"')
                else:
                    output.append(f'{k} = "{v}"')
            
            output.append("") # Spacer
            print("✅ Processed firebase_key.json")
        except Exception as e:
            print(f"❌ Error reading firebase_key.json: {e}")
    else:
        print("⚠️ firebase_key.json not found.")

    # 2. Process Web Config (.streamlit/secrets.toml)
    secrets_path = ".streamlit/secrets.toml"
    if os.path.exists(secrets_path):
        try:
            with open(secrets_path, 'r') as f:
                web_conf = f.read()
            
            output.append("# Copy from your local secrets.toml")
            output.append(web_conf)
            print(f"✅ Processed {secrets_path}")
        except Exception as e:
            print(f"❌ Error reading {secrets_path}: {e}")
    else:
        print(f"⚠️ {secrets_path} not found.")

    # Write to file
    with open('cloud_secrets.toml.txt', 'w') as f:
        f.write('\n'.join(output))
    
    print("\n🎉 DONE! Content saved to 'cloud_secrets.toml.txt'")
    print("👉 Open this file, copy EVERYTHING, and paste it into Streamlit Cloud -> App -> Settings -> Secrets")

if __name__ == "__main__":
    generate_secrets()
