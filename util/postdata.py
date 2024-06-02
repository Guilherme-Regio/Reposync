from requests import post, HTTPError, RequestException
from urllib3.exceptions import InsecureRequestWarning
from warnings import filterwarnings


filterwarnings('ignore', category=InsecureRequestWarning)

class PostData:
    def __init__(self, ip, data):
        if not isinstance(data, dict):
            data = {}
        data['reposync'] = True
        self.endpoint_url = '' # URL API ENDPOINT
        self.data = data
        self.headers = {'Content-Type': 'application/json'}
        self.send_update()


    def send_update(self):
        try:
            response = post(self.endpoint_url, json=self.data, headers=self.headers, verify=False)
            response.raise_for_status()
        except HTTPError as e:
            return False
        except RequestException as e:
            return False
        