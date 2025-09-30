CREATE TABLE Projects (id int primary key , name varchar(200));

CREATE TABLE Stages (id int primary key , name varchar(50));

CREATE TABLE States (id int primary key , name varchar(50));

CREATE TABLE Users (id int primary key , username varchar(100), email varchar(100), first_name varchar(100), last_name varchar(100));

CREATE TABLE Jobs (id int primary key,
                   assignee int,
                   stage_id int,
                   state_id int,
                   task_id int,
                   FOREIGN KEY (assignee) REFERENCES Users(id),
                   FOREIGN KEY (stage_id) REFERENCES Stages(id),
                   FOREIGN KEY (state_id) REFERENCES States(id),
                   FOREIGN KEY (task_id) REFERENCES Tasks(id));

CREATE TABLE Tasks (id int primary key,
                    name varchar(200),
                    project_id int,
                    FOREIGN KEY (project_id) REFERENCES Projects(id));

CREATE TABLE Reports (id int primary key,
                      user_id int,
                      datetime datetime,
                      jobs_count_today int,
                      jobs_count_all_finish int,
                      frames_count_today int,
                      frames_count_all_finish int,
                      shapes_count_today int,
                      shape_count_all int,
                      FOREIGN KEY (user_id) REFERENCES Users(id));

INSERT INTO Stages (id, name) VALUES (0, 'annotation'), (1, 'validation'), (2, 'acceptance');
INSERT INTO States (id, name) VALUES (0, 'new'), (1, 'in progress'), (2, 'rejected'), (3, 'completed');

INSERT INTO Tasks (id, name, project_id) VALUES (3, "test_termo", 1), (2, "test2", 1), (1, "test", 1)

ALTER TABLE Users RENAME COLUMN password TO first_name

ALTER TABLE Users ADD COLUMN last_name

ALTER TABLE Users DROP last_name

INSERT INTO Users (id, username, email, first_name, last_name)
VALUES (4, "abcabc", "abc@yandex.ru", "abc", "abc"),
(3, "aaaaa", "a@mail.ru", "af", "al"),
(2, "sdfghj", "sdfg@mail.ru", "jkjhkfgv", "fgfhgjnbhmn"),
(1, "user", "a@a.ru", "", "")

INSERT INTO Users (id, username, email, first_name, last_name)
VALUES (-1, "-", "-", "-", "-")

ALTER TABLE Jobs ADD CONSTRAINT fk_task_id_id FOREIGN KEY (task_id) REFERENCES Tasks(id)

DROP TABLE "Jobs"

SELECT max(id) FROM Reports WHERE user_id = 28 AND DATE(datetime) >= '2025-09-26' AND DATE(datetime) != '2025-09-29'

select date(datetime) from "Reports" where user_id = -1

SELECT datetime('now', 'localtime');

SELECT date(datetime(datetime, 'localtime')) FROM Reports WHERE user_id = 28

SELECT * FROM Reports WHERE DATE(datetime) = "2025-09-29" ORDER BY id DESC LIMIT 33

SELECT * FROM Tasks WHERE name LIKE '%_H20N_%'

CREATE TABLE Labels (id int primary key,
        name varchar(200),
        project_id int,
        FOREIGN KEY (project_id) REFERENCES Projects(id))

INSERT INTO Labels (id, name, project_id) VALUES (-1, "-", -1)

CREATE TABLE Presets (id int primary key,
        name varchar(500))

CREATE TABLE LabelsPresets (id INTEGER primary key AUTOINCREMENT,
        preset_id int,
        label_id int,
        FOREIGN KEY (preset_id) REFERENCES Presets(id),
        FOREIGN KEY (label_id) REFERENCES Labels(id))

CREATE TABLE LabelReports (id INTEGER primary key AUTOINCREMENT,
        report_id INTEGER,
        preset_id int,
        shapes_count_today int,
        shape_count_all int,
        FOREIGN KEY (report_id) REFERENCES Reports(id),
        FOREIGN KEY (preset_id) REFERENCES Presets(id))
