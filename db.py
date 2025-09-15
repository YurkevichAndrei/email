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

    def __init_db__(self):
        cursor = self.db.cursor()

        request = 'CREATE TABLE Projects (id int primary key , name varchar(200))'
        cursor.execute(request)
        self.db.commit()

        request = 'CREATE TABLE Stages (id int primary key , name varchar(50))'
        cursor.execute(request)
        self.db.commit()

        request = 'CREATE TABLE States (id int primary key , name varchar(50))'
        cursor.execute(request)
        self.db.commit()

        request = 'CREATE TABLE Users (id int primary key , username varchar(100), email varchar(100), first_name varchar(100), last_name varchar(100))'
        cursor.execute(request)
        self.db.commit()

        request = '''CREATE TABLE Jobs (id int primary key,
        assignee int,
        stage_id int,
        state_id int,
        task_id int,
        FOREIGN KEY (assignee) REFERENCES Users(id),
        FOREIGN KEY (stage_id) REFERENCES Stages(id),
        FOREIGN KEY (state_id) REFERENCES States(id),
        FOREIGN KEY (task_id) REFERENCES Tasks(id))'''
        cursor.execute(request)
        self.db.commit()

        request = '''CREATE TABLE Tasks (id int primary key,
        name varchar(200),
        project_id int,
        FOREIGN KEY (project_id) REFERENCES Projects(id))'''
        cursor.execute(request)
        self.db.commit()

        request = '''CREATE TABLE Reports (id int primary key,
        user_id int,
        datetime datetime,
        jobs_count_today int,
        jobs_count_all_finish int,
        frames_count_today int,
        frames_count_all_finish int,
        shapes_count_today int,
        shape_count_all int,
        FOREIGN KEY (user_id) REFERENCES Users(id))'''
        cursor.execute(request)
        self.db.commit()

        request = 'INSERT INTO Stages (id, name) VALUES (0, "annotation"), (1, "validation"), (2, "acceptance")'
        cursor.execute(request)
        self.db.commit()

        request = 'INSERT INTO States (id, name) VALUES (0, "new"), (1, "in progress"), (2, "rejected"), (3, "completed")'
        cursor.execute(request)
        self.db.commit()

        request = 'INSERT INTO Users (id, username, email, first_name, last_name) VALUES (-1, "-", "-", "-", "-")'
        cursor.execute(request)
        self.db.commit()

    # методы инициализаций таблиц нужно переделать под обновления,
    # чтобы можно было использовать при добавлении новых данных
    def __init_db_projects__(self):
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

    def __init_db_tasks__(self):
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

    def __init_db_users__(self):
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

    def __init_db_jobs__(self):
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

    def init_db(self):
        self.__init_db__()
        self.__init_db_projects__()
        self.__init_db_tasks__()
        self.__init_db_users__()
        self.__init_db_jobs__()

db = DataBase()
db.init_db()
# db.init_db_users()
# db.init_db_projects()
# db.init_db_tasks()