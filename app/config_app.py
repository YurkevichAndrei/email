import hashlib
import streamlit as st
import json
import os
from extra_streamlit_components import CookieManager
import requests


class ConfigurationApp:
    def __init__(self):
        self.cookie_manager = CookieManager()
        self.config = self.load_config()
        self.server_path = f"{self.config['report']['server']['host']}:{self.config['report']['server']['port']}"

    # Функция проверки авторизации
    @staticmethod
    def check_auth(login: str, password):
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        stored_hash = "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918"  # hash для 'admin'

        return login == "admin" and password_hash == stored_hash

    # Загрузка конфигурации приложения
    @staticmethod
    def load_config():
        try:
            if os.path.exists('config'):
                with open('config', 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass

        # Конфигурация по умолчанию
        default_config = {
            "cvat": {
                "url": "http://neuron.npomis.ru:8080",
                "user": {
                    "username": "spopov",
                    "email": "spopov@npomis.ru",
                    "password": "C6hd4z4n!"
                }
            },
            "email": {
                "sender": {
                    "username": "ayurkevich",
                    "email": "ayurkevich@npomis.ru",
                    "password": "ePu9ahga"
                },
                "recipient": {
                    "email": "ad6803884@yandex.ru"
                }
            }
        }
        return default_config

    # Функция выхода
    def logout(self):
        st.session_state.authenticated = False
        st.session_state.persistent_auth = False
        st.session_state.config_updated = False

        # Удаляем cookie
        try:
            self.cookie_manager.delete('admin_auth')
        except:
            pass

        st.rerun()

    # Функция входа
    def login(self, login: str, password, remember_me=False):
        if self.check_auth(login, password):
            st.session_state.authenticated = True
            st.session_state.persistent_auth = remember_me
            # Сохраняем в cookies если выбрано "Запомнить меня"
            if remember_me:
                try:
                    # Устанавливаем cookie на 30 дней
                    import datetime
                    expires_at = datetime.datetime.now() + datetime.timedelta(days=30)
                    self.cookie_manager.set('admin_auth', 'authenticated_admin_session', expires_at=expires_at)
                except:
                    st.warning("Не удалось сохранить сессию в cookies")

            url = f"{self.server_path}/db/update"
            response = requests.get(url)
            if response:
                pass
            st.rerun()
        else:
            st.error("❌ Неверный логин или пароль")

    # Сохранение конфигурации
    @staticmethod
    def save_config(config):
        with open('config', 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)

    # Функция применения изменений
    def apply_changes(self):
        self.save_config(st.session_state.app_config)
        st.rerun()
        # st.success("✅ Конфигурация приложения успешно обновлена!")
        # time.sleep(5)
        # st.rerun()

    # Проверяем авторизацию через cookies
    def check_cookie_auth(self):
        try:
            auth_cookie = self.cookie_manager.get('admin_auth')
            if auth_cookie:
                # Проверяем подпись (простая проверка для демо)
                return auth_cookie == "authenticated_admin_session"
        except:
            pass
        return False

    @staticmethod
    def find_key_by_value(data, value, field):
        for key, item in data.items():
            if item.get(field) == value:
                return key
        return None

    @staticmethod
    def custom_spinner(message="Пожалуйста, подождите..."):
        """Кастомный спиннер"""
        st.markdown(f"""
        <div class="loading-container">
            <div class="custom-spinner"></div>
            <p>{message}</p>
        </div>
        """, unsafe_allow_html=True)

    def generate_report(self):
        st.session_state.generate_report = False
        url = f"{self.server_path}/report/new"
        requests.get(url)

    @staticmethod
    def click_generate_report():
        st.session_state.generate_report = True

    @staticmethod
    def on_change_project():
        st.session_state.change_project = True

    @staticmethod
    def change_project_f(new_name, names_list, proj_ids):
        st.session_state.project = proj_ids[names_list.index(new_name)]

    def app(self):
        st.set_page_config(
            page_title="Отчеты CVAT",  # Заголовок для вкладки браузера
            page_icon="⚙️",              # Иконка для вкладки
            layout="wide"                # Растягивание на весь экран
        )

        # Инициализация cookies (выполняется один раз)
        if not hasattr(st, 'cookie_manager_initialized'):
            try:
                # Пытаемся инициализировать cookie manager
                if hasattr(self.cookie_manager, 'get_all'):
                    st.cookie_manager_initialized = True
            except:
                pass

        # Инициализация сессии с проверкой cookies
        if 'authenticated' not in st.session_state:
            # Проверяем, есть ли сохраненная сессия в cookies
            if self.check_cookie_auth():
                st.session_state.authenticated = True
                st.session_state.persistent_auth = True
            else:
                st.session_state.authenticated = False
                st.session_state.persistent_auth = False

        if 'app_config' not in st.session_state:
            st.session_state.app_config = self.load_config()

        if 'generate_report' not in st.session_state:
            st.session_state.generate_report = False

        if 'change_project' not in st.session_state:
            st.session_state.change_project = False

        if 'project' not in st.session_state:
            st.session_state.project = st.session_state.app_config['report']['project']

        if 'labels' not in st.session_state:
            st.session_state.labels = {}

        # Если не авторизован - показываем форму входа
        if not st.session_state.authenticated:
            st.markdown("""
            <style>
            .stMainBlockContainer {
                max-width: 50%;
                padding-left: 5rem;
                padding-right: 5rem;
            }
            </style>
            """, unsafe_allow_html=True)
            st.title("🔐 Авторизация")

            with st.form("auth_form"):
                login_input = st.text_input("Логин", placeholder="Введите логин", value="admin")
                password_input = st.text_input("Пароль", type="password", placeholder="Введите пароль", value="admin")
                remember_me = st.checkbox("Запомнить меня", value=True)

                submitted = st.form_submit_button("Войти", type="primary")

                if submitted:
                    self.login(login_input, password_input, remember_me)

            # st.info("💡 Для входа используйте: **логин: admin, пароль: admin**")

            st.stop()  # Останавливаем выполнение дальше

        # Информация о сессии в сайдбаре
        with st.sidebar:
            st.write(f"**Вы вошли как:** admin")

            if st.button("🚪 Выйти"):
                self.logout()

            st.button("Сгенерировать отчёт", on_click=self.click_generate_report, type="primary")
            if st.session_state.generate_report:
                spinner_container = st.empty()
                # Показываем спиннер в контейнере
                with spinner_container.container():
                    self.custom_spinner("Собираем статистику и генерируем отчет...")
                self.generate_report()
                # Очищаем контейнер
                spinner_container.empty()
                st.success("Готово!")

        # Инициализация конфигурации в session_state
        if 'config' not in st.session_state:
            st.session_state.app_config = self.load_config()

        # Настройка страницы ДО любых других команд Streamlit
        st.set_page_config(layout="wide")

        # Применение кастомных стилей для растягивания на весь экран
        st.markdown("""
            <style>
            .stMainBlockContainer {
                max-width: 90%;
                padding-left: 5rem;
                padding-right: 5rem;
            }
            </style>
            """, unsafe_allow_html=True)

        config_container = st.container()
        with (config_container):
            # Кастомный CSS для красивого спиннера
            st.markdown("""
            <style>
            .custom-spinner {
                display: inline-block;
                width: 50px;
                height: 50px;
                border: 5px solid #f3f3f3;
                border-top: 5px solid #1E88E5;
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin: 20px auto;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            .loading-container {
                text-align: center;
                padding: 20px;
            }
            
            .fixed-header {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                background-color: #0E1117;
                color: white;
                padding: 15px 0;
                text-align: center;
                z-index: 9999;
                font-size: 1.5rem;
                font-weight: bold;
                box-shadow: 0 2px 10px rgba(0,0,0,0.2);
            }
            /* Добавляем отступ для основного контента */
            .main-content {
                margin-top: 80px;
            }
            """, unsafe_allow_html=True)

            # Интерфейс
            st.title("⚙️ Панель управления конфигурацией приложения")

            #
            # st.markdown("### Текущая конфигурация")
            # st.json(st.session_state.app_config, expanded=False)

            # CSS для увеличения шрифта во вкладках
            st.markdown("""
                <style>
                    /* Подпункты */
                    button[data-baseweb="tab"] > div[data-testid="stMarkdownContainer"] {
                        font-size: 1.0rem;
                    }
                    /* Пункты */
                    button[data-baseweb="tab"] > div[data-testid="stMarkdownContainer"] > p {
                        font-size: 1.2rem;
                    }
                </style>
                """, unsafe_allow_html=True)
            st.markdown("### Изменение параметров приложения")

            # Создаем форму для всех полей
            with st.form("app_config_form"):

                tab1, tab2= st.tabs(["Настройки отчетов", "Настройки CVAT"])

                with tab1:
                    tab11, tab12, tab13, tab14, tab15, tab16 = st.tabs(["Отправитель", "Получатели", "Хранение",
                                                                        "Пользователи", "Пресеты", "Проект"])
                    with tab11:
                        sender_username = st.text_input(
                            "Имя пользователя",
                            value=st.session_state.app_config['email']['sender']['username'],
                            key="sender_username_input"
                        )

                        sender_email = st.text_input(
                            "Email пользователя",
                            value=st.session_state.app_config['email']['sender']['email'],
                            key="sender_email_input"
                        )

                        sender_password = st.text_input(
                            "Пароль пользователя",
                            value=st.session_state.app_config['email']['sender']['password'],
                            type='password',
                            key="sender_password_input"
                        )

                    with tab12:
                        recipient_emails = st.multiselect(
                            'Адреса пользователей',
                            options=st.session_state.app_config['email']['recipient']['emails'],
                            default=st.session_state.app_config['email']['recipient']['emails'],
                            key="recipients_email_input",
                            accept_new_options=True
                        )

                    with tab13:
                        report_folder_path = st.text_input(
                            "Папка для отчетов",
                            value=st.session_state.app_config['report']['folder_path'],
                            key="report_folder_path_input"
                        )

                    with tab14:
                        cb_users = {}
                        url = f"{self.server_path}/db/users"
                        response = requests.get(url)
                        users = response.json()
                        col1, col2 = st.columns(2)
                        users_list = list(users.items())
                        for index, (user_id, user) in enumerate(users_list):
                            user_id = int(user_id)
                            value = False
                            if user_id in st.session_state.app_config['report']['users']:
                                value = True
                            # Выбираем колонку в зависимости от четности индекса
                            current_col = col1 if index % 2 == 0 else col2
                            # Размещаем чекбокс в выбранной колонке
                            with current_col:
                                report_user = st.checkbox(
                                    user['name'],
                                    value=value,
                                    key=f"report_users_{user_id}_input"
                                )
                                cb_users[user['name']] = report_user

                    with tab15:
                        # Инициализация данных в session_state
                        if 'presets' not in st.session_state:
                            st.session_state.presets = {}
                        url = f"{self.server_path}/db/presets"
                        response = requests.get(url)
                        st.session_state.presets = response.json()
                        if st.session_state.presets.get('detail') == 'Not Found':
                            st.session_state.presets = {}
                        else:
                            st.session_state.presets = {int(i): preset for i, preset in st.session_state.presets.items()}
                        # st.session_state.presets = {
                        #     0: {
                        #         "name": "пресет 1",
                        #         "labels": []
                        #     },
                        #     1: {
                        #         "name": "пресет 2",
                        #         "labels": []
                        #     },
                        #     2: {
                        #         "name": "пресет 3",
                        #         "labels": []
                        #     },
                        #     3: {
                        #         "name": "пресет 4",
                        #         "labels": []
                        #     },
                        # }
                        if st.form_submit_button("Добавить пресет", key="new_button"):
                            max_id_preset = 0
                            if len(list(st.session_state.presets.keys())) != 0:
                                max_id_preset = max(list(st.session_state.presets.keys()))
                            new_preset = {'name': "Новый пресет", "labels": []}
                            st.session_state.presets[max_id_preset+1] = new_preset
                            st.rerun()

                        if len(list(st.session_state.presets.keys())) != 0:
                            preset_ids = list(st.session_state.presets.keys())

                            url = f"{self.server_path}/db/labels"
                            response = requests.get(url, params={'project_id': st.session_state.project})
                            st.session_state.labels = response.json()

                            for i in preset_ids:
                                # Проверяем, существует ли еще пресет (мог быть удален в предыдущей итерации)
                                if i not in st.session_state.presets.keys():
                                    continue
                                with st.expander(st.session_state.presets[i]['name']):
                                    st.session_state.presets[i]['name'] = st.text_input("Имя", value=st.session_state.presets[i]['name'], key=f"name_{i}")
                                    st.session_state.presets[i]['labels'] = st.multiselect(
                                        "Выберите опции",
                                        st.session_state.labels.keys(),
                                        default=st.session_state.presets[i]['labels'],
                                        key=f"select_{i}"
                                        )
                                    if st.form_submit_button("Удалить пресет", key=f"del_button_{i}"):
                                        st.session_state.presets.pop(i)
                                        st.rerun()

                    with tab16:
                        url = f"{self.server_path}/db/projects"
                        response = requests.get(url)
                        projects = response.json()

                        projects_nums = []
                        i = 0
                        options = []
                        index = 0
                        for id_proj, proj_name in projects.items():
                            id_proj = int(id_proj)
                            options.append(proj_name)
                            projects_nums.append(id_proj)
                            if id_proj == st.session_state.project:
                                index = i
                            i+=1

                        option = st.selectbox(
                            "Выберите проект:",
                            options,
                            index=index,
                            on_change=self.on_change_project()
                        )
                        if st.session_state.change_project:
                            self.change_project_f(option, options, projects_nums)
                            st.session_state.change_project = False

                with tab2:
                    url_cvat = st.text_input(
                        "Хост CVAT",
                        value=st.session_state.app_config['cvat']['url'],
                        key="url_cvat_input"
                    )

                    st.markdown("###### Настройки доступа")

                    username = st.text_input(
                        "Имя пользователя",
                        value=st.session_state.app_config['cvat']['user']['username'],
                        key="username_input"
                    )

                    email = st.text_input(
                        "Email пользователя",
                        value=st.session_state.app_config['cvat']['user']['email'],
                        key="email_input"
                    )

                    password = st.text_input(
                        "Пароль пользователя",
                        value=st.session_state.app_config['cvat']['user']['password'],
                        type='password',
                        key="password_input"
                    )

                # Кнопка применения изменений
                submitted = st.form_submit_button("💾 Применить изменения", type="primary")

                if submitted:
                    # Обновляем конфигурацию в session_state
                    st.session_state.app_config['cvat']['url'] = url_cvat

                    st.session_state.app_config['cvat']['user']['username'] = username
                    st.session_state.app_config['cvat']['user']['email'] = email
                    st.session_state.app_config['cvat']['user']['password'] = password

                    st.session_state.app_config['email']['sender']['username'] = sender_username
                    st.session_state.app_config['email']['sender']['email'] = sender_email
                    st.session_state.app_config['email']['sender']['password'] = sender_password

                    st.session_state.app_config['email']['recipient']['emails'] = recipient_emails

                    st.session_state.app_config['report']['folder_path'] = report_folder_path

                    report_users = []
                    for name, cb in cb_users.items():
                        if cb:
                            user_id = self.find_key_by_value(users, name, 'name')
                            if user_id is None:
                                continue
                            report_users.append(int(user_id))

                    st.session_state.app_config['report']['users'] = report_users

                    st.session_state.app_config['report']['presets'] = list(st.session_state.presets.keys())

                    presets = {}
                    if len(list(st.session_state.presets.keys())) != 0:
                        preset_ids = list(st.session_state.presets.keys())

                        for i in preset_ids:
                            # Проверяем, существует ли еще пресет (мог быть удален в предыдущей итерации)
                            if i not in st.session_state.presets.keys():
                                continue
                            presets[i] = {'name': st.session_state.presets[i]['name'], 'labels': []}
                            for label in st.session_state.presets[i]['labels']:
                                presets[i]['labels'].append(st.session_state.labels[label])

                    url = f"{self.server_path}/db/presets"
                    requests.post(url, json=presets)

                    self.apply_changes()

if __name__ == '__main__':
    app = ConfigurationApp()
    app.app()
