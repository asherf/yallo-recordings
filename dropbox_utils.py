
from oauth2client import client
from oauth2client import tools
import oauth2client
import dropbox
from file_utils import get_secrets_file_path

DROPBOX_CLIENT_SECRET_FILE = 'dropbox_client_secret.json'
ACCOUNT_CREDS_FILE = 'yallo-recordings-grabber-dropbox.json'
APPLICATION_NAME = 'Yallo Recordings Grabber'

class DropboxCredentials(object):

    def __init__(self, access_token, user_id):
        self._access_token = access_token
        self._user_id = user_id

    def set_store(self, store):
        pass

    def to_json(self):
        cls = type(self)
        return json.dumps(dict(access_token=self._access_token, user_id=self._user_id,
                               _module=cls.__module__, _class=cls.__name__))

    @classmethod
    def from_json(cls, data):
        data = json.loads(data)
        return DropboxCredentials(access_token=data['access_token'], user_id=data['user_id'])


class DropboxOAuth2Flowable(client.Flow):
    def __init__(self, app_key, app_secret):
        self._flow = None
        self._app_key = app_key
        self._app_secret = app_secret
        self.redirect_uri = None  # set by tools.run_flow
        self._session = dict()
        self._csrf_token_key = "csrf_dropbox_token"

    def step1_get_authorize_url(self, redirect_uri=None, state=None):
        if not self.redirect_uri:
            raise Exception("no redirect URI set")
        self._flow = dropbox.client.DropboxOAuth2Flow(self._app_key, self._app_secret, self.redirect_uri,
                                                      self._session, self._csrf_token_key)
        auth_url = self._flow.start()
        return auth_url

    def step2_exchange(self, code=None, http=None, device_flow_info=None):
        import ipdb; ipdb.set_trace()
        access_token, user_id, url_state = self._flow.finish(dict(code=code, state=self._session[self._csrf_token_key]))
        return DropboxCredentials(access_token, user_id)


def auth_dropbox():
    credential_path = get_secrets_file_path(ACCOUNT_CREDS_FILE)
    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials:
        dropbox_secrets = json.loads(open(get_secrets_file_path(DROPBOX_CLIENT_SECRET_FILE)).read())
        flow = DropboxOAuth2Flowable(dropbox_secrets['app_key'], dropbox_secrets['app_secret'])
        #authorize_url = flow.start()
        credentials = tools.run_flow(flow, store, argparse.ArgumentParser(parents=[tools.argparser]).parse_args())
        print('Storing credentials to ' + credential_path)
    return credentials
