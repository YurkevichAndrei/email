import requests
import json

config = {}

def load_config():
    global config
    with open('config', 'r') as config_file:
        config = json.load(config_file)

def analize():
    user = {"user": config["user"]["username"], "email": config["user"]["email"], "password": config["user"]["password"]}
    url = '%s/api/auth/login'%(config["url_cvat"])
    response = requests.post(url, json=user)
    if response.status_code == 200:
        cookies = response.cookies

        url = '%s/api/jobs/2'%(config["url_cvat"])

        response = requests.get(url, cookies=cookies)

        print(response.json())


def main():
    load_config()
    analize()

main()
