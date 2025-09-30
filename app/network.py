import requests
import json

import logging


class Networking:
    def __init__(self):
        self.config = {}
        self.load_config()
        self.session = requests.session()
        self.headers = {}
        self.log = logging
        self.log.basicConfig(level=logging.INFO, filename="log.log",filemode="w")

    def load_config(self):
        with open('config', 'r') as config_file:
            self.config = json.load(config_file)

    def init_session(self):
        user = {"username": self.config["cvat"]["user"]["username"], "email": self.config["cvat"]["user"]["email"], "password": self.config["cvat"]["user"]["password"]}
        url = '%s/api/auth/login'%(self.config["cvat"]["url"])

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
        url = '%s/api/auth/logout'%(self.config["cvat"]["url"])
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
        url = '%s/api/projects'%(self.config["cvat"]["url"])
        try:
            response = self.session.get(url, params=[('page_size', 200)])
        except:
            return None
        print(response.json())
        return response.json()

    def get_tasks(self):
        url = '%s/api/tasks'%(self.config["cvat"]["url"])
        try:
            response = self.session.get(url, params=[('page_size', 2000)])
        except:
            return None
        print(response.json())
        return response.json()

    def get_users(self):
        url = '%s/api/users'%(self.config["cvat"]["url"])
        try:
            response = self.session.get(url, params=[('page_size', 200)])
        except:
            return None
        print(response.json())
        return response.json()

    def get_jobs(self):
        url = '%s/api/jobs'%(self.config["cvat"]["url"])
        try:
            response = self.session.get(url, params=[('page_size', 200)])
        except:
            return None
        print(response.json())
        return response.json()

    def get_job(self, job_id):
        url = '%s/api/jobs/%d'%(self.config["cvat"]["url"], job_id)
        try:
            response = self.session.get(url, params=[('page_size', 5000)])
        except:
            return None
        print(response.json())
        return response.json()

    def get_job_annotations(self, job_id: int):
        url = '%s/api/jobs/%d/annotations'%(self.config["cvat"]["url"], job_id)
        try:
            response = self.session.get(url, params=[('page_size', 2000)])
        except:
            return None
        self.log.info(response.json()['shapes'])
        return response.json()

    def get_labels(self, job_id: int = None):
        url = '%s/api/labels'%(self.config["cvat"]["url"])
        params = [('page_size', 500)]
        if not (job_id is None):
            params.append(('job_id', job_id))
        try:
            response = self.session.get(url, params=params)
        except:
            return None
        print(response.json())
        return response.json()

# net = Networking()
# net.init_session()
# net.get_labels()
# net.close_session()