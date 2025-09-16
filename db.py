import sqlite3
import os

from network import Networking
# from parameters_selection import ParametersSelection

class DataBase:
    def __init__(self):
        self.network = Networking()
        self.network.init_session()

        db_file = 'reports_cvat__.db'
        if os.path.isfile(db_file):
            self.db = sqlite3.connect(db_file)
        else:
            self.db = sqlite3.connect(db_file)
            self.init_db()

    def __del__(self):
        self.network.close_session()
        self.db.close()

    def insert(self, table_name: str, params: list[str], values: str):
        params = ', '.join([p for p in params])
        request = 'INSERT INTO %s (%s) VALUES %s' % (table_name, params, values)
        cursor = self.db.cursor()
        cursor.execute(request)
        self.db.commit()

    def select(self, table_name: str, columns: list[str], constraints: list[str] = ()):
        request = f'SELECT {', '.join([c for c in columns])} FROM {table_name}'
        if len(constraints) != 0:
            constr = ' AND '.join([c for c in constraints])
            request = ' WHERE '.join([request, constr])
        cursor = self.db.cursor()
        cursor.execute(request)
        return cursor.fetchall()

    def create_db(self):
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
    def update_db_projects(self):
        if self.db is None:
            return False
        projects = self.network.get_projects()['results']

        only_in_id_list = self.difference_list_id('Projects', projects)

        data = ''
        for project in projects:
            if project['id'] in only_in_id_list:
                separator = ', '
                if data == '':
                    separator = ''
                data = separator.join([data, '(%d, "%s")' % (project['id'], project['name'])])
        self.insert('Projects', ['id', 'name'], data)

    def update_db_tasks(self):
        if self.db is None:
            return False
        tasks = self.network.get_tasks()['results']

        only_in_id_list = self.difference_list_id('Tasks', tasks)

        data = ''
        for task in tasks:
            if task['id'] in only_in_id_list:
                separator = ', '
                if data == '':
                    separator = ''
                data = separator.join([data, '(%d, "%s", %d)' % (task['id'], task['name'], task['project_id'])])

        self.insert('Tasks', ['id', 'name', 'project_id'], data)

    def update_db_users(self):
        if self.db is None:
            return False
        users = self.network.get_users()['results']

        # нужно сначала получить полный список id, потом сравнить с результатами запроса
        only_in_id_list = self.difference_list_id('Users', users)

        data = ''
        for user in users:
            if user['id'] in only_in_id_list:
                separator = ', '
                if data == '':
                    separator = ''
                data = separator.join([data, '(%d, "%s", "%s", "%s", "%s")' % (user['id'], user['username'], user['email'], user['first_name'], user['last_name'])])

        self.insert('Users', ['id', 'username', 'email', 'first_name', 'last_name'], data)

    def update_db_jobs(self):
        if self.db is None:
            return False
        stages = {'annotation': 0, 'validation': 1, 'acceptance': 2}
        states = {'new': 0, 'in progress': 1, 'rejected': 2, 'completed': 3}
        jobs = self.network.get_jobs()['results']

        # нужно сначала получить полный список id, потом сравнить с результатами запроса
        only_in_id_list = self.difference_list_id('Jobs', jobs)

        data = ''
        for job in jobs:
            # params = ParametersSelection()
            # params.add_equal('id', job['id'], type(job['id']))
            # constrains = params.get_parameters_selection()
            # selection = self.__select__('Jobs', ['id'], constrains)
            # # если объект по id найдет, то переходим на следующую итерацию
            # if len(selection) == 0:
            #     continue
            if job['id'] in only_in_id_list:
                separator = ', '
                if data == '':
                    separator = ''
                assignee = job['assignee']
                assignee_id = -1
                if not (assignee is None):
                    assignee_id = assignee['id']
                data = separator.join([data, '(%d, %d, %d, %d, %d)' % (job['id'], assignee_id, stages[job['stage']], states[job['state']], job['task_id'])])

        self.insert('Jobs', ['id', 'assignee', 'stage_id', 'state_id', 'task_id'], data)

    def init_db(self):
        self.create_db()
        self.update_db_projects()
        self.update_db_tasks()
        self.update_db_users()
        self.update_db_jobs()

    def difference_list_id(self, table_name: str, objects):
        id_list = sorted([obj['id'] for obj in objects])
        selection = sorted(self.select(table_name, ['id']))
        return set(id_list) - set(selection)

#TODO дальше нужно реализовать формирования записей в таблице reports

db = DataBase()
db.init_db()
# db.init_db_users()
# db.init_db_projects()
# db.init_db_tasks()