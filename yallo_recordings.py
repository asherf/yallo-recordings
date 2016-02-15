import httplib2
import base64
import os
import json
import argparse
import urlparse
import requests
from bs4 import BeautifulSoup
from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools
import dropbox

from google_utils import get_gmail_service


DROPBOX_FOLDER = "/Users/afoa/Dropbox/Yallo"
#import yallo_recordings as yallo; yallo.auth_dropbox()


def download_recordings():
    links = get_links()
    open("yallo_links.json", "w").write(json.dumps(links))



def get_links():
    service = get_gmail_service()

    #results = service.users().labels().list(userId='me').execute()
    #labels = results.get('labels', [])

    # find yallo label
    msgs_svc = service.users().messages()

    response = msgs_svc.list(userId='me', labelIds='Label_37').execute()
    links = list()
    for msg in response['messages']:
        msg_data = msgs_svc.get(userId='me', id=msg['id']).execute()
        print "get recording link for %s" % msg_data['snippet']
        link = get_recording_link(msg_data)
        links.append(dict(link=link, subject=msg_data['snippet']))
    return links


def get_recording_link(msg):

    htmldoc = base64.urlsafe_b64decode(msg['payload']['parts'][1]['body']['data'].encode('ASCII'))
    soup = BeautifulSoup(htmldoc, 'html.parser')
    rec = [link.get("href") for link in soup.find_all('a') if "listen" in link.text.lower()]
    if not rec:
        raise Exception("can't find recording link")
    url = urlparse.urlparse(rec[0])
    response = requests.get("%s://%s%s" % (url.scheme, url.netloc, url.path), params=urlparse.parse_qs(url.query))
    response.raise_for_status()
    if "s3.amazonaws.com/yalo-recordings" in response.url:
        return response.url
    share_id = urlparse.parse_qs(urlparse.urlparse(response.url).query)['share_id'][0]
    url = "https://socialism-online.appspot.com/_ah/api/users/v1/get_call_details_by_share"
    response = requests.post(url, json=dict(share_id=share_id))
    response.raise_for_status()
    return response.json()['recording_url']
