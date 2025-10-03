from fastapi import FastAPI

from db import DataBase
from main import Report

db = DataBase()
rep = Report()

app = FastAPI()

@app.get("/db/update")
def update_db():
    return db.update_db()

@app.get("/db/users")
def db_get_users():
    users = db.get_users()
    print(users)
    return users

@app.get("/report/new")
def generate_report():
    return rep.daily_task()

@app.get("/db/projects")
def db_get_projects():
    projects = db.get_projects()
    print(projects)
    return projects

@app.get("/db/labels")
def db_get_labels(project_id: int):
    labels = db.get_labels(project_id)
    print(labels)
    return labels