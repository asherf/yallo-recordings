
import os
def get_secrets_file_path(filename):
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    return os.path.join(credential_dir, filename)
