import hashlib
import streamlit as st
import json
import os
from extra_streamlit_components import CookieManager

from db import DataBase
from main import Report

cookie_manager = CookieManager()
db = DataBase()


# Функция проверки авторизации
def check_auth(login: str, password):
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    stored_hash = "8c6976e5b5410415bde908bd4dee15dfb167a9c873fc4bb8a81f6f2ab448a918"  # hash для 'admin'

    return login == "admin" and password_hash == stored_hash


# Загрузка конфигурации приложения
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
def logout():
    st.session_state.authenticated = False
    st.session_state.persistent_auth = False
    st.session_state.config_updated = False

    # Удаляем cookie
    try:
        cookie_manager.delete('admin_auth')
    except:
        pass

    st.rerun()

# Функция входа
def login(login: str, password, remember_me=False):
    if check_auth(login, password):
        st.session_state.authenticated = True
        st.session_state.persistent_auth = remember_me
        # Сохраняем в cookies если выбрано "Запомнить меня"
        if remember_me:
            try:
                # Устанавливаем cookie на 30 дней
                import datetime
                expires_at = datetime.datetime.now() + datetime.timedelta(days=30)
                cookie_manager.set('admin_auth', 'authenticated_admin_session', expires_at=expires_at)
            except:
                st.warning("Не удалось сохранить сессию в cookies")

        db.update_db()
        st.rerun()
    else:
        st.error("❌ Неверный логин или пароль")

# Сохранение конфигурации
def save_config(config):
    with open('config', 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=4)

# Функция применения изменений
def apply_changes():
    save_config(st.session_state.app_config)
    st.rerun()
    # st.success("✅ Конфигурация приложения успешно обновлена!")
    # time.sleep(5)
    # st.rerun()

# Проверяем авторизацию через cookies
def check_cookie_auth():
    try:
        auth_cookie = cookie_manager.get('admin_auth')
        if auth_cookie:
            # Проверяем подпись (простая проверка для демо)
            return auth_cookie == "authenticated_admin_session"
    except:
        pass
    return False

def find_key_by_value(data, value, field):
    for key, item in data.items():
        if item.get(field) == value:
            return key
    return None

def generate_report():
    st.session_state.generate_report = False
    rep = Report()
    rep.daily_task()

def click_generate_report():
    st.session_state.generate_report = True

def app():
    # Инициализация cookies (выполняется один раз)
    if not hasattr(st, 'cookie_manager_initialized'):
        try:
            # Пытаемся инициализировать cookie manager
            if hasattr(cookie_manager, 'get_all'):
                st.cookie_manager_initialized = True
        except:
            pass

    # Инициализация сессии с проверкой cookies
    if 'authenticated' not in st.session_state:
        # Проверяем, есть ли сохраненная сессия в cookies
        if check_cookie_auth():
            st.session_state.authenticated = True
            st.session_state.persistent_auth = True
        else:
            st.session_state.authenticated = False
            st.session_state.persistent_auth = False

    if 'app_config' not in st.session_state:
        st.session_state.app_config = load_config()

    if 'generate_report' not in st.session_state:
        st.session_state.generate_report = False

    # Если не авторизован - показываем форму входа
    if not st.session_state.authenticated:
        st.title("🔐 Авторизация")

        with st.form("auth_form"):
            login_input = st.text_input("Логин", placeholder="Введите логин", value="admin")
            password_input = st.text_input("Пароль", type="password", placeholder="Введите пароль", value="admin")
            remember_me = st.checkbox("Запомнить меня", value=True)

            submitted = st.form_submit_button("Войти", type="primary")

            if submitted:
                login(login_input, password_input, remember_me)

        # st.info("💡 Для входа используйте: **логин: admin, пароль: admin**")

        st.stop()  # Останавливаем выполнение дальше

    # Информация о сессии в сайдбаре
    with st.sidebar:
        st.write(f"**Вы вошли как:** admin")

        st.button("Сгенерировать отчёт", on_click=click_generate_report, type="primary")

        if st.session_state.generate_report:
            generate_report()

        if st.button("🚪 Выйти"):
            logout()

    # Инициализация конфигурации в session_state
    if 'config' not in st.session_state:
        st.session_state.app_config = load_config()
    config_container = st.container()
    with (config_container):
        # Интерфейс
        st.title("⚙️ Панель управления конфигурацией приложения")


        st.markdown("### Текущая конфигурация")
        st.json(st.session_state.app_config, expanded=False)


        st.markdown("### Изменение параметров приложения")

        # Создаем форму для всех полей
        with st.form("app_config_form"):
            st.markdown("#### Настройки отчетов")
            st.markdown("##### Отправитель")
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

            st.markdown("##### Получатели")
            recipient_emails = st.multiselect(
                'Адреса пользователей',
                options=st.session_state.app_config['email']['recipient']['emails'],
                default=st.session_state.app_config['email']['recipient']['emails'],
                key="recipients_email_input",
                accept_new_options=True
            )

            st.markdown("##### Хранение")
            report_folder_path = st.text_input(
                "Папка для отчетов",
                value=st.session_state.app_config['report']['folder_path'],
                key="report_folder_path_input"
            )

            st.markdown("##### Пользователи")

            cb_users = {}
            users = db.get_users()
            for user_id, user in users.items():
                value = False
                if user_id in st.session_state.app_config['report']['users']:
                    value = True
                report_user = st.checkbox(
                    user['name'],
                    value=value,
                    key=f"report_users_{user_id}_input"
                )
                cb_users[user['name']] = report_user

            st.markdown("#### Настройки CVAT")

            url_cvat = st.text_input(
                "Хост CVAT",
                value=st.session_state.app_config['cvat']['url'],
                key="url_cvat_input"
            )

            st.markdown("##### Настройки доступа")

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
                        user_id = find_key_by_value(users, name, 'name')
                        if user_id is None:
                            continue
                        report_users.append(user_id)

                st.session_state.app_config['report']['users'] = report_users

                apply_changes()

if __name__ == '__main__':
    app()
