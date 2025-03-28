### I could not complete this script because I do not have access to the HCP CLI or the specific environment setup.
# This script is designed to authenticate with HCP (HashiCorp Cloud Platform), check if the user is authenticated,
# and if not, attempt to authenticate. It also reads a secret from HCP Vault using the HCP CLI.
#!/usr/bin/env python3

import subprocess
import os
import time
import config
from dotenv import load_dotenv

def check_hcp_auth():
    """Checks if the user is authenticated with HCP."""
    try:
        result = subprocess.run(["hcp", "whoami"], capture_output=True, text=True, check=True)
        # If 'hcp whoami' succeeds, the user is authenticated.
        return True
    except subprocess.CalledProcessError:
        # If 'hcp whoami' fails, the user is not authenticated.
        return False
    except FileNotFoundError:
        print("Error: hcp command not found. Make sure it's installed and in your PATH.")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False

def authenticate_hcp():
    """Authenticates the user with HCP."""
    try:
        my_env = os.environ.copy()
        hcp_bin_path = "/home/linuxbrew/.linuxbrew/bin"  # Or /usr/local/bin if needed.
        if hcp_bin_path not in my_env["PATH"]:
            my_env["PATH"] = f"{hcp_bin_path}:{my_env['PATH']}"

        print(f"Updated PATH: {my_env['PATH']}")  # Debugging line
        subprocess.run(["hcp", "auth", "login"], check=True, env=my_env)
        print("HCP authentication successful.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"HCP authentication failed: {e.stderr}")  # Debugging line
        return False
    except FileNotFoundError:
        print("Error: hcp command not found. Make sure it's installed and in your PATH.")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False

def main():
    # Construct the path to the .env file in Folder A
    print(f"Loading environment variables from: {config.ENV_FILE_PATH}")  # Debugging line to check the path
    load_dotenv(dotenv_path=config.ENV_FILE_PATH)
    #load_dotenv(dotenv_path=dotenv_path)
    secret_name = os.getenv("OPENAI_SECRET_NAME")
	
    if check_hcp_auth():
        print("1. Hello, authenticated HCP user!")
    else:
        print("You are not authenticated with HCP. Attempting login...")
        if authenticate_hcp():
            print("2. , authenticated HCP user!")
        else:
            print("Authentication failed. Cannot print hello.")

    try:
        sec = subprocess.run(["hcp", "vault-secrets", "secrets", "open", secret_name], check=True)
        print(sec)
        return sec
    except subprocess.CalledProcessError:
        print("Failed to open secret.")
        return None
    except FileNotFoundError:   
        print("Error: hcp command not found. Make sure it's installed and in your PATH.")
        return None
    except Exception as e:  
        print(f"An unexpected error occurred: {e}")
        return None


if __name__ == "__main__":
    print(os.environ)
    main()
