import requests
from urllib.parse import urljoin
import re
import time

ALLOWED_REQUEST_TYPES = ['get', 'post']
DEFAULT_URL = 'http://127.0.0.1:888/'
DEFAULT_HEADERS = {'User-Agent': 'Mozilla/5.0', 'Content-Type': 'application/x-www-form-urlencoded'}
PHPBB_LOGIN_EXTRA_URL = "ucp.php?mode=login"
LOG_FILENAME = 'log.txt'

def getKwRequestType(dic):
    if 'type' in dic:
        type = dic['type']
    else:
        type = 'get'
    if type not in ALLOWED_REQUEST_TYPES:
        strn = '{} is not a valid type'.format(type)
        raise ValueError(strn)
    return type
        
def getKwPayload(dic):
    if 'payload' in dic:
        payload = dic['payload']
    else:
        payload = {}
    return payload

def getKwUrl(dic):
    if 'url' in dic:
        url = dic['url']
    else:
        url = DEFAULT_URL
    return url

class Browser(object):
    @property
    def url(self): return self._url
    
    @url.setter
    def url(self, val):
        self._url = val

    @property
    def session(self): return self._session
    
    @session.setter
    def session(self, val):
        if val is None:
            self._session = requests.Session()
            self.headers = DEFAULT_HEADERS
        else:
            self._session = val
    

    def __init__(self, url=None, session=None):
        self.session = session
        self.url = url
        self.type = 'generic'

    def writelog(self, resp, filename=LOG_FILENAME):
        with open(filename, 'w', encoding="utf-8") as f:
            f.write(resp.text)

    def get_form_fields(self, url):
        resp = self.request(url=url, type='get')
        text = resp.text
        match = re.findall('form_token" value="(\w+)"', text)
        form_token = match[0]
        match = re.findall('creation_time" value="(\w+)"', text)
        creation_time = match[0]
        data = {
                'form_token': form_token,
                'creation_time': creation_time,
                }
        return data
        
    def login(self, baseurl, username, password):
        print('Starting login procedures ...')
        print('Loading the login form ...')
        form_fields = self.get_form_fields(baseurl);
        url = urljoin(baseurl, PHPBB_LOGIN_EXTRA_URL)
        payload = {'username': username, 'password': password, 'login':'Login'}
        payload.update(form_fields)
        resp = self.request(url=url, type='post', payload=payload)
        return resp
    
    def isLoggedIn(self):
        bLogged = len(self.session.cookies) > 0
        if (bLogged):
            print(f'Checking login status ... already logged in')
        else:
            print(f'Checking login status ... Not logged in')
        return bLogged

    def request(self, **kwargs):
        session = self.session
        type = getKwRequestType(kwargs)
        url = getKwUrl(kwargs)
        payload = getKwPayload(kwargs)
        if type == 'get':
            print(f'>> GET: {url}')
            resp = session.get(url, headers=self.headers)
        elif type == 'post':
            print(f'>> POST: {url}  using payload {payload}')
            resp = session.post(url, headers=self.headers, data=payload)
        else:
            resp = None
        print('Sleeping for 3 seconds to wait for the response ...')
        time.sleep(3)
        return resp
