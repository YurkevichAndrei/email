CREATE TABLE Projects (id int primary key , name varchar(200));

CREATE TABLE Stages (id int primary key , name varchar(50));

CREATE TABLE States (id int primary key , name varchar(50));

CREATE TABLE Users (id int primary key , username varchar(100), email varchar(100), password varchar(200));

CREATE TABLE Jobs (id int primary key ,
                   assignee int,
                   stage_id int,
                   state_id int,
                   task_id int,
                   FOREIGN KEY (assignee) REFERENCES Users(id),
                   FOREIGN KEY (stage_id) REFERENCES Stages(id),
                   FOREIGN KEY (state_id) REFERENCES States(id));

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