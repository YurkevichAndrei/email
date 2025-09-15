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

    def __insert__(self, tabel_name, params, values):
        params = ', '.join([p for p in params])
        request = 'INSERT INTO %s (%s) VALUES %s' % (tabel_name, params, values)
        cursor = self.db.cursor()
        cursor.execute(request)
        self.db.commit()

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
        self.__insert__('Projects', ['id', 'name'], data)

    def init_db_tasks(self):
        if self.db is None:
            return False
        tasks = self.network.get_tasks()['results']
        data = ''
        for task in tasks:
            separator = ', '
            if data == '':
                separator = ''
            data = separator.join([data, '(%d, "%s", %d)' % (task['id'], task['name'], task['project_id'])])

        self.__insert__('Tasks', ['id', 'name', 'project_id'], data)

    def init_db_users(self):
        if self.db is None:
            return False
        users = self.network.get_users()['results']
        data = ''
        for user in users:
            separator = ', '
            if data == '':
                separator = ''
            data = separator.join([data, '(%d, "%s", "%s", "%s", "%s")' % (user['id'], user['username'], user['email'], user['first_name'], user['last_name'])])

        self.__insert__('Users', ['id', 'username', 'email', 'first_name', 'last_name'], data)

    def init_db_jobs(self):
        if self.db is None:
            return False
        stages = {'annotation': 0, 'validation': 1, 'acceptance': 2}
        states = {'new': 0, 'in progress': 1, 'rejected': 2, 'completed': 3}
        jobs = self.network.get_jobs()['results']
        data = ''
        for job in jobs:
            separator = ', '
            if data == '':
                separator = ''
            assignee = job['assignee']
            assignee_id = -1
            if not (assignee is None):
                assignee_id = assignee['id']
            data = separator.join([data, '(%d, %d, %d, %d, %d)' % (job['id'], assignee_id, stages[job['stage']], states[job['state']], job['task_id'])])

        self.__insert__('Jobs', ['id', 'assignee', 'stage_id', 'state_id', 'task_id'], data)

db = DataBase()
db.init_db_jobs()
# db.init_db_users()
# db.init_db_projects()
# db.init_db_tasks()