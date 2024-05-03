import sys

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Define the scopes for accessing Gmail data
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

# Path to OAuth 2.0 credentials file
CLIENT_SECRET_FILE = 'client_secret.json'

# Redirect URI used in OAuth consent screen
REDIRECT_URI = 'http://localhost:8080/'


def obtain_access_token():
    # Create flow instance using OAuth 2.0 client ID and client secret
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)

    try:
        # Run local server to handle OAuth callback
        flow.run_local_server()

        # Get access token
        credentials = flow.credentials
        if not credentials.refresh_token:
            new_credentials = Credentials(token=credentials.token, refresh_token=credentials.token)
            for field in vars(credentials):
                if field not in ['_refresh_token', '_token']:
                    setattr(new_credentials, field, getattr(credentials, field))
            credentials = new_credentials

        return credentials
    except Exception as e:
        print("An error occurred:", e)
        sys.exit(1)


# Example usage
if __name__ == '__main__':
    access_token = obtain_access_token()
    print('Access token:', access_token)
