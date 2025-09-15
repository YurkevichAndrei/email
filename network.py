import requests
import json


class Networking:
    def __init__(self):
        self.config = {}
        # self.cookies = ''
        self.load_config()
        self.session = requests.session()
        self.headers = {}

    def load_config(self):
        with open('config', 'r') as config_file:
            self.config = json.load(config_file)

    def init_session(self):
        user = {"user": self.config["user"]["username"], "email": self.config["user"]["email"], "password": self.config["user"]["password"]}
        url = '%s/api/auth/login'%(self.config["url_cvat"])

        try:
            response = self.session.post(url, json=user)
        except:
            return False
        self.headers = {'X-CSRFToken': self.session.cookies.get('csrftoken')}
        print(self.session.cookies.get('csrftoken'))
        if response.status_code == 200:
            return True
        else:
            return False

    def close_session(self):
        url = '%s/api/auth/logout'%(self.config["url_cvat"])
        try:
            response = self.session.post(url, headers=self.headers)
        except:
            return False
        print(response.json())
        if response.status_code == 200:
            return True
        else:
            return False

    def get_projects(self):
        url = '%s/api/projects'%(self.config["url_cvat"])
        try:
            response = self.session.get(url)
        except:
            return None
        print(response.json())
        return response.json()

    def get_tasks(self):
        url = '%s/api/tasks'%(self.config["url_cvat"])
        try:
            response = self.session.get(url)
        except:
            return None
        print(response.json())
        return response.json()

    def get_users(self):
        url = '%s/api/users'%(self.config["url_cvat"])
        try:
            response = self.session.get(url)
        except:
            return None
        print(response.json())
        return response.json()

    def get_jobs(self):
        url = '%s/api/jobs'%(self.config["url_cvat"])
        try:
            response = self.session.get(url)
        except:
            return None
        print(response.json())
        return response.json()

# net = Networking()
# net.init_session()
# net.get_jobs()
# net.close_session()