import requests
import json


class Networking:
    def __init__(self):
        self.config = {}
        self.cookies = ''
        self.load_config()

    def load_config(self):
        with open('config', 'r') as config_file:
            self.config = json.load(config_file)

    def init_session(self):
        user = {"user": self.config["user"]["username"], "email": self.config["user"]["email"], "password": self.config["user"]["password"]}
        url = '%s/api/auth/login'%(self.config["url_cvat"])
        try:
            response = requests.post(url, json=user)
        except:
            return False
        if response.status_code == 200:
            self.cookies = response.cookies
            return True
        else:
            return False

    def close_session(self):
        url = '%s/api/auth/logout'%(self.config["url_cvat"])
        try:
            response = requests.post(url, cookies=self.cookies)
        except:
            return False
        print(response.json())
        if response.status_code == 200:
            self.cookies = response.cookies
            return True
        else:
            return False

    def get_projects(self):
        url = '%s/api/projects'%(self.config["url_cvat"])
        try:
            response = requests.get(url, cookies=self.cookies)
        except:
            return None
        print(response.json())
        return response.json()

# net = Networking()
# net.init_session()
# net.get_projects()
# net.close_session()