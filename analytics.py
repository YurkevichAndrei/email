import sqlite3



def init_session():
    global cookies
    user = {"user": config["user"]["username"], "email": config["user"]["email"], "password": config["user"]["password"]}
    url = '%s/api/auth/login'%(config["url_cvat"])
    response = requests.post(url, json=user)
    if response.status_code == 200:
        cookies = response.cookies


def analize():
    global cookies
    url = '%s/api/jobs/2'%(config["url_cvat"])

    response = requests.get(url, cookies=cookies)

    print(response.json())

    db = sqlite3.connect('reports_cvat.db')

    cursor = db.cursor()

    # request =

    # cursor.execute('')

    db.close()




def main():
    load_config()
    analize()

main()
