CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE,
    password TEXT
);

CREATE TABLE groups (
    id SERIAL PRIMARY KEY,
    name TEXT,
    visible BOOLEAN
);

CREATE TABLE sports (
    id SERIAL PRIMARY KEY,
    name TEXT
);

CREATE TABLE routes (
    id SERIAL PRIMARY KEY,
    name TEXT,
    length INTEGER,
    visible BOOLEAN
);

CREATE TABLE activities (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users,
    sport_id INTEGER REFERENCES sports,
    route_id INTEGER REFERENCES routes,
    duration INT,
    date TEXT,
    visible BOOLEAN
);

CREATE TABLE groupmembers (
    id SERIAL PRIMARY KEY,
    group_id INTEGER REFERENCES groups,
    user_id INTEGER REFERENCES users,
    visible BOOLEAN
);

CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    activity_id INTEGER REFERENCES activities,
    user_id INTEGER REFERENCES users,
    content TEXT,
    date TEXT,
    seen BOOLEAN,
    visible BOOLEAN
);

INSERT INTO routes (name, length, visible) VALUES ('PRESET | 5km', 5, TRUE);
INSERT INTO routes (name, length, visible) VALUES ('PRESET | 7.5km', 7.5, TRUE);
INSERT INTO routes (name, length, visible) VALUES ('PRESET | 10km', 10, TRUE);
INSERT INTO routes (name, length, visible) VALUES ('PRESET | 15km', 15, TRUE);
INSERT INTO routes (name, length, visible) VALUES ('PRESET | 20km', 20, TRUE);
INSERT INTO routes (name, length, visible) VALUES ('PRESET | 21.1km', 21.1, TRUE);
INSERT INTO routes (name, length, visible) VALUES ('PRESET | 30km', 30, TRUE);
INSERT INTO routes (name, length, visible) VALUES ('PRESET | 40km', 40, TRUE);
INSERT INTO routes (name, length, visible) VALUES ('PRESET | 40.2km', 40.2, TRUE);
INSERT INTO routes (name, length, visible) VALUES ('PRESET | 60km', 60, TRUE);
INSERT INTO routes (name, length, visible) VALUES ('PRESET | 80km', 80, TRUE);

INSERT INTO groups (name, visible) VALUES ('TKO-Äly', TRUE);
INSERT INTO groups (name, visible) VALUES ('Pohjoisen Parhaat', TRUE);
INSERT INTO groups (name, visible) VALUES ('Imperials', TRUE);

INSERT INTO sports (name) VALUES ('walk');
INSERT INTO sports (name) VALUES ('run');
INSERT INTO sports (name) VALUES ('cycling');