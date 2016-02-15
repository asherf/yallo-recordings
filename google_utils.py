
from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools
from file_utils import get_secrets_file_path

SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
GOOGLE_CLIENT_SECRET_FILE = 'google_client_secret.json'
ACCOUNT_CREDS_FILE = 'yallo-recordings-grabber.json'

def auth_gmail():
    credential_path = get_secrets_file_path(ACCOUNT_CREDS_FILE)

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(get_secrets_file_path(GOOGLE_CLIENT_SECRET_FILE), SCOPES)
        flow.user_agent = APPLICATION_NAME
        credentials = tools.run_flow(flow, store, argparse.ArgumentParser(parents=[tools.argparser]).parse_args())
        print('Storing credentials to ' + credential_path)
    return credentials

def get_gmail_service():
    credentials = auth_gmail()
    http = credentials.authorize(httplib2.Http())
    return  discovery.build('gmail', 'v1', http=http)
