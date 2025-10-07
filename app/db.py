import sqlite3
import os
import datetime

from network import Networking
from parameters_selection import ParametersSelection

class DataBase:
    def __init__(self):
        self.network = Networking()
        self.network.init_session()
        self.db = None

        db_file = 'reports_cvat_neuron.db'
        if os.path.isfile(db_file):
            self.db = sqlite3.connect(db_file, timeout=30.0, check_same_thread=False)
            # self.update_db()
        else:
            self.db = sqlite3.connect(db_file, timeout=30.0, check_same_thread=False)
            self.init_db()

    def __del__(self):
        self.network.close_session()
        # self.db.close()

    def insert(self, table_name: str, params: list[str], values: str):
        if values != '':
            params = ', '.join([p for p in params])
            request = 'INSERT INTO %s (%s) VALUES %s' % (table_name, params, values)
            print(request)
            self.network.log.info(request)
            cursor = self.db.cursor()
            cursor.execute(request)
            cursor.close()
            self.db.commit()

    def select(self, table_name: str, columns: list[str] = (), constraints: list[str] = (), sorting: list[str] = (), limit: int = None):
        request = ''
        if len(columns) != 0:
            request = f'SELECT {', '.join([c for c in columns])} FROM {table_name}'
        else:
            request = f'SELECT * FROM {table_name}'

        if len(constraints) != 0:
            constr = ' AND '.join([c for c in constraints])
            request = ' WHERE '.join([request, constr])

        if len(sorting) != 0:
            constr = ', '.join([s for s in sorting])
            request = ' ORDER BY '.join([request, constr])

        if not (limit is None):
            request = ' LIMIT '.join([request, str(limit)])

        self.network.log.info(request)
        cursor = self.db.cursor()
        cursor.execute(request)
        res = cursor.fetchall()
        cursor.close()
        return res

    def delete(self, table_name: str, constraints: list[str] = ()):
        request = f'DELETE FROM {table_name}'

        if len(constraints) != 0:
            constr = ' AND '.join([c for c in constraints])
            request = ' WHERE '.join([request, constr])

        self.network.log.info(request)
        cursor = self.db.cursor()
        cursor.execute(request)
        cursor.close()
        self.db.commit()

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

        request = 'CREATE TABLE Users (id int primary key , username varchar(100), first_name varchar(100), last_name varchar(100))'
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

        request = '''CREATE TABLE Labels (id int primary key,
        name varchar(200),
        project_id int,
        FOREIGN KEY (project_id) REFERENCES Projects(id))'''
        cursor.execute(request)
        self.db.commit()

        request = '''CREATE TABLE Reports (id INTEGER primary key AUTOINCREMENT,
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

        request = '''CREATE TABLE LabelReports (id INTEGER primary key AUTOINCREMENT,
        report_id INTEGER,
        label_id int,
        shapes_count_today int,
        shape_count_all int,
        FOREIGN KEY (report_id) REFERENCES Reports(id),
        FOREIGN KEY (label_id) REFERENCES Labels(id))'''
        cursor.execute(request)
        self.db.commit()

        request = 'INSERT INTO Stages (id, name) VALUES (0, "annotation"), (1, "validation"), (2, "acceptance")'
        cursor.execute(request)
        self.db.commit()

        request = 'INSERT INTO States (id, name) VALUES (0, "new"), (1, "in progress"), (2, "rejected"), (3, "completed")'
        cursor.execute(request)
        self.db.commit()

        request = 'INSERT INTO Projects (id, name) VALUES (-1, "-")'
        cursor.execute(request)
        self.db.commit()

        request = 'INSERT INTO Tasks (id, name, project_id) VALUES (-1, "-", -1)'
        cursor.execute(request)
        self.db.commit()

        request = 'INSERT INTO Labels (id, name, project_id) VALUES (-1, "-", -1)'
        cursor.execute(request)
        self.db.commit()

        request = 'INSERT INTO Users (id, username, first_name, last_name) VALUES (-1, "-", "-", "-")'
        cursor.execute(request)
        self.db.commit()
        cursor.close()

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
                project_id = -1
                if not (task['project_id'] is None):
                    project_id = task['project_id']
                data = separator.join([data, '(%d, "%s", %d)' % (task['id'], task['name'], project_id)])

        self.insert('Tasks', ['id', 'name', 'project_id'], data)

    def update_db_labels(self):
        if self.db is None:
            return False
        labels = self.network.get_labels()['results']

        only_in_id_list = self.difference_list_id('Labels', labels)

        data = ''
        for label in labels:
            if label['id'] in only_in_id_list:
                separator = ', '
                if data == '':
                    separator = ''
                project_id = -1
                if not (label.get('project_id') is None):
                    project_id = label['project_id']
                data = separator.join([data, '(%d, "%s", %d)' % (label['id'], label['name'], project_id)])

        self.insert('Labels', ['id', 'name', 'project_id'], data)

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
                data = separator.join([data, '(%d, "%s", "%s", "%s")' % (user['id'], user['username'], user['first_name'], user['last_name'])])

        self.insert('Users', ['id', 'username', 'first_name', 'last_name'], data)

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
                task_id = -1
                if not (job['task_id'] is None):
                    task_id = job['task_id']
                data = separator.join([data, '(%d, %d, %d, %d, %d)' % (job['id'], assignee_id, stages[job['stage']], states[job['state']], task_id)])

        self.insert('Jobs', ['id', 'assignee', 'stage_id', 'state_id', 'task_id'], data)

    def init_db(self):
        self.create_db()
        self.update_db_projects()
        self.update_db_tasks()
        self.update_db_labels()
        self.update_db_users()
        self.update_db_jobs()

    def update_db(self):
        self.update_db_projects()
        self.update_db_tasks()
        self.update_db_labels()
        self.update_db_users()
        self.update_db_jobs()
        return True

    def difference_list_id(self, table_name: str, objects):
        id_list = sorted([obj['id'] for obj in objects])
        selection = sorted(self.select(table_name, ['id']))
        selection = [select[0] for select in selection]
        return set(id_list) - set(selection)

    def update_db_reports(self):
        if self.db is None:
            return False

        reports = self.generate_reports()
        print(reports)

        last_id = self.select('Reports', ['max(id)'])[0][0] + 1

        values_list = []
        # расчет количества элементов списков и внесение изменений в бд
        for assignee_id, report in reports.items():
            ps = ParametersSelection()
            ps.add_equal('user_id', assignee_id, value_type=type(assignee_id))
            date = datetime.date.today() - datetime.timedelta(days=3)
            ps.add_inequal(field_name='DATE(datetime)', value=date, more_less=True, and_equal=True, value_type=type(date))
            ps.add_inequal(field_name='DATE(datetime)', value=datetime.date.today(), more_less=False, and_equal=False, value_type=type(date))
            # id последнего отчета для пользователя assignee_id
            selection = self.select('Reports', ['max(id)'], ps.get_parameters_selection())
            # print(selection)
            last_id_report_user = -1
            values = ''
            # если уже есть отчет для пользователя assignee_id
            if not (selection[0][0] is None):
                last_id_report_user = selection[0][0]
                # надо взять данные прошлого отчета и вычесть их из вчерашних данных, получим данные за прошедший период
                ps1 = ParametersSelection()
                # id последнего отчета для пользователя assignee_id
                ps1.add_equal('id', last_id_report_user, value_type=type(last_id_report_user))
                selection_all_params = self.select('Reports',
                                                   ['jobs_count_all_finish', 'frames_count_all_finish', 'shape_count_all'],
                                                   ps1.get_parameters_selection())
                values = '(%d, %d, %s, %d, %d, %d, %d, %d, %d)' % (last_id,
                                                                   assignee_id,
                                                                   "datetime('now')",
                                                                   len(report['jobs']) - selection_all_params[0][0],
                                                                   len(report['jobs']),
                                                                   len(report['frames']) - selection_all_params[0][1],
                                                                   len(report['frames']),
                                                                   len(report['shapes']) - selection_all_params[0][2],
                                                                   len(report['shapes']))

            # TODO тут нужно придумать как сделать запись в LabelReports
            # для каждого пресета сформировать отчет (если пресеты есть)
            # скорее всего это лучше вынести в отдельный метод

            # если отчетов нет
            else:
                values = '(%d, %d, %s, %d, %d, %d, %d, %d, %d)' % (last_id, assignee_id, "datetime('now')",
                                                                   len(report['jobs']), len(report['jobs']),
                                                                   len(report['frames']), len(report['frames']),
                                                                   len(report['shapes']), len(report['shapes']))
            values_list.append(values)
            last_id += 1

        #     для указанного шейпа нужно проверить есть ли все указанные в пресете тэги
        #     смотрим отчет для данного пользователя и проходимся по всем пресетам

        values = ', '.join(values_list)
        self.insert('Reports', ['id', 'user_id', 'datetime', 'jobs_count_today', 'jobs_count_all_finish',
                                    'frames_count_today', 'frames_count_all_finish', 'shapes_count_today', 'shape_count_all'], values)

    @staticmethod
    def add_if_not_exists(lst, value):
        """
        Проверяет, есть ли значение в списке.
        Если нет - добавляет и возвращает новый список.
        Если есть - возвращает список без изменений.

        Args:
            lst (list): Входной список
            value: Значение для проверки и добавления

        Returns:
            list: Обновленный список или исходный список
        """
        if value not in lst:
            # Создаем копию списка, чтобы не изменять оригинал
            new_list = lst.copy()
            new_list.append(value)
            return new_list
        else:
            return lst

    def generate_reports(self):
        # {
        #     1: {
        #         'jobs': [1, 2, 3 ...],
        #         'frames': [1, 2, 3 ...],
        #         'shapes': [shape_and_labels, shape_and_labels, shape_and_labels ...]
        #     },
        #     2: {
        #         'jobs': [1, 2, 3 ...],
        #         'frames': [1, 2, 3 ...],
        #         'shapes': [shape_and_labels, shape_and_labels, shape_and_labels ...]
        #     },
        # }
        # сбор информации о количестве задач, изображений и объектов
        reports = {}
        jobs = self.network.get_jobs()['results']
        for job in jobs:
            assignee = job['assignee']
            assignee_id = -1
            if not (assignee is None):
                assignee_id = assignee['id']

            annotations = self.network.get_job_annotations(job['id'])

            # shape_and_labels
            # {
            #     frame_id: [
            #         label_id,
            #         label_id
            #     ],
            #     frame_id: [
            #         label_id,
            #         label_id
            #     ]
            # }

            # перед тем как формировать словарь по объектам, нужно сформировать словарь с тегами по фреймам
            labels = {}
            for label in annotations['tags']:
                if labels.get(label['frame']) is None:
                    labels[label['frame']] = [label['label_id']]
                else:
                    labels[label['frame']].append(label['label_id'])

            if reports.get(assignee_id) is None:
                reports[assignee_id] = {'jobs': [], 'frames': [], 'shapes': []}

            report = reports.get(assignee_id)
            report['jobs'] = self.add_if_not_exists(report['jobs'], job['id'])

            for shape in annotations['shapes']:
                report['frames'] = self.add_if_not_exists(report['frames'], f'{job['id']}:{shape['frame']}')
                labs = labels.get(shape['frame'])
                shape_and_labels = {}
                if labs is None:
                    shape_and_labels = {'shape': shape['id'], 'labels': [shape['label_id']]}
                else:
                    shape_and_labels = {'shape': shape['id'], 'labels': labs}
                    shape_and_labels['labels'].append(shape['label_id'])
                report['shapes'] = self.add_if_not_exists(report['shapes'], shape_and_labels)
            reports[assignee_id] = report
        return reports

    def get_users(self):
        selections = self.select('Users')
        users = {}
        for s in selections:
            if s[0] == -1: # id
                continue
            # last_name first_name username
            user = {'name': f'{s[3]} {s[2]}', 'username': s[1]}
            # id
            users[s[0]] = user
        return users

    def get_reports(self, date: datetime.date = datetime.date.today()):
        self.update_db_reports()
        count_users = self.select('Users', ['count(*)'])[0][0]
        date = date.isoformat()
        ps = ParametersSelection()
        ps.add_equal("DATE(datetime)", date, value_type=type(date))
        reports = {}
        selections = self.select(table_name='Reports', constraints=ps.get_parameters_selection(), sorting=['id DESC'], limit=count_users)

        for s in selections:
            if s[1] == -1: # user_id
                continue
            report = {'Задачи': s[3], 'Изображения': s[5], 'Объекты': s[7]}
            # user_id
            reports[s[1]] = report
        return reports

    def get_projects(self):
        selections = self.select('Projects')
        projects = {}
        for s in selections:
            if s[0] == -1: # id
                continue
            # id
            projects[s[0]] = s[1]
        return projects

    def get_labels(self, project_id):
        ps = ParametersSelection()
        ps.add_equal("project_id", project_id, value_type=type(project_id))
        selections = self.select('Labels', columns=['id', 'name'], constraints=ps.get_parameters_selection())
        labels = {}
        for s in selections:
            if s[0] == -1: # id
                continue
            labels[s[1]] = s[0]
        return labels

    def get_presets(self):
        # SELECT p.id, p.name, l.name
        # FROM Presets as p, LabelsPresets as lp, Labels as l
        # WHERE lp.id == p.id AND lp.label_id == l.id
        ps = ParametersSelection()
        ps.add_equal('lp.preset_id', 'p.id', value_type=int)
        ps.add_equal('lp.label_id', 'l.id', value_type=int)
        selections = self.select('Presets as p, LabelsPresets as lp, Labels as l',
                                 columns=['p.id', 'p.name', 'l.name'],
                                 constraints=ps.get_parameters_selection())
        presets = {}
        for s in selections:
            if presets.get(s[0]) is None:
                presets[s[0]] = {'name': s[1], 'labels': [s[2]]}
            else:
                presets[s[0]]['labels'].append(s[2])
        print(presets)
        return presets

    def set_presets(self, presets: dict):
        print(presets)
        #  проверка нет ли пресета с таким id
        #  если есть, то удалить все labelsPresets, которые с ним связаны, и добавить обновленные
        #  если нет, то просто добавляем пресет по полной
        presets_db = [s[0] for s in self.select(table_name='Presets', columns=['id'])]
        for i, preset in presets.items():
            # если пресет с таким id уже существует
            if i in presets_db:
                ps = ParametersSelection()
                ps.add_equal("preset_id", i, value_type=type(i))
                self.delete(table_name='LabelsPresets', constraints=ps.get_parameters_selection())
                ps1 = ParametersSelection()
                ps1.add_equal("id", i, value_type=type(i))
                self.delete(table_name='Presets', constraints=ps1.get_parameters_selection())

            data = f'({i}, "{preset['name']}")'
            self.insert(table_name="Presets", params=['id', 'name'], values=data)

            data = ''
            for label in preset['labels']:
                separator = ', '
                if data == '':
                    separator = ''
                data = separator.join([data, f'({i}, {label})'])
            self.insert(table_name="LabelsPresets", params=['preset_id', 'label_id'], values=data)


# db = DataBase()
# db.update_db()