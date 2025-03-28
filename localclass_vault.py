import requests
import os
from dotenv import load_dotenv
#import config
import service_codehelpers.config as config

class HCPAuthenticator:
    """Class to handle HCP authentication and token retrieval."""

    def __init__(self):
        """
        Initialize the HCPAuthenticator with the path to the .env file.
        :param env_file_path: Path to the .env file containing credentials.
        """
        self.env_file_path = config.ENV_FILE_PATH
        self.hcp_client_id = None
        self.hcp_client_secret = None
        self.token_url = None
        self._load_env_variables()

    def _load_env_variables(self):
        """Load environment variables from the specified .env file."""
        print(f"Loading environment variables from: {self.env_file_path}")  # Debugging line
        load_dotenv(dotenv_path=self.env_file_path)

        self.hcp_client_id = os.getenv("HCP_CLIENT_ID")
        #print(f"HCP_CLIENT_ID: {self.hcp_client_id}")  # Debugging line

        self.hcp_client_secret = os.getenv("HCP_CLIENT_SECRET")
        #print(f"HCP_CLIENT_SECRET: {self.hcp_client_secret}")  # Debugging line

        self.token_url = os.getenv("HCP_TOKEN_ENDPOINT")
        #print(f"Token URL: {self.token_url}")  # Debugging line

        self.secret_url = os.getenv("HCP_SECRET_URL")

        if not self.hcp_client_id or not self.hcp_client_secret:
            raise ValueError("HCP_CLIENT_ID or HCP_CLIENT_SECRET not found in .env")

    def get_token(self):
        """
        Retrieve an HCP token using client credentials.
        :return: Access token as a string, or None if retrieval fails.
        """
        data = {
            "grant_type": "client_credentials",
            "client_id": self.hcp_client_id,
            "client_secret": self.hcp_client_secret,
        }

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }

        # Make a POST request to retrieve the token
        try:
            response = requests.post(self.token_url, headers=headers, data=data)
            response.raise_for_status()
            token_data = response.json()
            return token_data["access_token"]
        except requests.exceptions.HTTPError as e:
            print(f"HTTP error: {e}")
            print(response.text)
            return None
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            return None
        except KeyError as e:
            print(f"Key error: {e}, likely bad response format")
            return None
        
    def get_secret(self):
        """
        Retrieve a secret from the HCP Vault using the access token.
        :param access_token: The access token for authentication.
        :param secret_url: The URL to retrieve the secret.
        :return: The secret data as a dictionary, or None if retrieval fails.
        """
        access_token = self.get_token()
        if not access_token:
            print("Failed to retrieve access token.")
            return None
        secret_url = self.secret_url
        if not secret_url:
            print("Secret URL is not set.")
            return None
        
        headers = {
            "Authorization": f"Bearer {access_token}",
        }

        try:
            response = requests.get(secret_url, headers=headers)
            response.raise_for_status()
            secret_data = response.json()
            secret_value = secret_data['secrets'][0]['static_version']['value']
            return secret_value
        except requests.exceptions.HTTPError as e:
            print(f"HTTP error: {e}")
            print(response.text)
            return None
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            return None
        except KeyError as e:
            print(f"Key error: {e}, likely bad response format")
            return None


# Example usage:
if __name__ == "__main__":
    print("Retrieving HCP token...")

    # Instantiate the authenticator with the path to the .env file
    authenticator = HCPAuthenticator()

    # Call the method to get the HCP token
    token = authenticator.get_token()
    if token:
        print(f"HCP Token: {token}")
        print()
        print("Retrieving secret data...")
        # Use the token for subsequent HCP API requests
        secret_data = authenticator.get_secret()
        if secret_data:
            print(secret_data)
        else:
            print("Failed to retrieve secret data.")
    else:
        print("Failed to retrieve HCP token.")