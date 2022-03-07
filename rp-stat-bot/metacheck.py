import requests
from time import sleep


class Base(object):

    def __init__(self, session=None, env=None, project=None):
        self.endpoint = env[project]['METABASE_URL'] + 'api'
        self.email = env[project]['METABASE_EMAIL']
        self.password = env[project]['METABASE_PASSWORD']
        self.session = session
        if self.session is None:
            self.session = self.auth()

    def session_header(self):
        #print(self.session)
        return {'X-Metabase-Session': self.session}

    def get_session_headers(self, *args, **kwargs):
        res = requests.get(self.endpoint + '/user/current',
                           headers=self.session_header())
        if res.status_code == 401:
            self.auth()
        return self.session_header()

    def fetch_header(self, response):
        if response.status_code == 200:
            return True
        else:
            return False

    def fetch_body(self, response):
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, None

    def get(self, *args, headers=None, **kwargs):
        headers = self.get_session_headers(headers, kwargs)
        response = requests.get(self.endpoint + args[0], headers=headers, **kwargs)
        #print(response.json())
        return self.fetch_body(response)

    def post(self, *args, json=None, headers=None, **kwargs):
        headers = self.get_session_headers(headers, kwargs)
        response = requests.post(self.endpoint + args[0], json=json, headers=headers, **kwargs)
        #print(response.json())
        return self.fetch_body(response)

    def put(self, *args,  json=None, headers=None, **kwargs):
        headers = self.get_session_headers(headers, kwargs)
        response = requests.put(self.endpoint + args[0], headers=headers, json=json, **kwargs)
        #print(response.json())
        return self.fetch_header(response)

    def delete(self, *args, headers=None, **kwargs):
        headers = self.get_session_headers(headers, kwargs)
        response = requests.delete(self.endpoint + args[0], headers=headers, **kwargs)
        #print(response.json())
        return self.fetch_header(response)

    def auth(self):
        payload = {'username': self.email,
                   'password': self.password}
        for retry in range(0, 6):
            res = requests.post(self.endpoint + '/session', json=payload)
            if res.status_code == 200:
                data = res.json()
                session = data['id']
                return session
            elif res.status_code == 500:
                pass
            elif res.status_code == 400:
                print('Metabase 400 ERROR. Wait 120s...')
                sleep(120)
            else:
                raise Exception(res)

