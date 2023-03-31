CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE,
    password TEXT
);

CREATE TABLE groups (
    id SERIAL PRIMARY KEY,
    name TEXT
);

CREATE TABLE sports (
    id SERIAL PRIMARY KEY,
    name TEXT
);

CREATE TABLE routes (
    id SERIAL PRIMARY KEY,
    name TEXT,
    length INTEGER
);

CREATE TABLE activities (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users,
    sport_id INTEGER REFERENCES sports,
    route_id INTEGER REFERENCES routes,
    duration INT,
    date TEXT
);

CREATE TABLE groupmembers (
    id SERIAL PRIMARY KEY,
    group_id INTEGER REFERENCES groups,
    user_id INTEGER REFERENCES users
);

CREATE TABLE comments (
    id SERIAL PRIMARY KEY,
    activity_id INTEGER REFERENCES activities,
    user_id INTEGER REFERENCES users,
    content TEXT,
    date TEXT
);

