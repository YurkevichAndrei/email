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
