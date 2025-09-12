import sqlite3

from network import Networking

class DataBase:
    def __init__(self):
        self.network = Networking()
        self.network.init_session()
        try:
            self.db = sqlite3.connect('reports_cvat.db')
        except:
            self.db = None

    # def __del__(self):
    #     self.network.close_session()
    #     self.db.close()

    def init_db_projects(self):
        if self.db is None:
            return False
        projects = self.network.get_projects()['results']
        data = ''
        for project in projects:
            separator = ', '
            if data == '':
                separator = ''
            data = separator.join([data, '(%d, "%s")' % (project['id'], project['name'])])

        request = 'INSERT INTO Projects (id, name) VALUES %s' % data
        cursor = self.db.cursor()
        cursor.execute(request)
# INSERT INTO Projects (id, name) VALUES


# cursor.execute('')

db = DataBase()
db.init_db_projects()