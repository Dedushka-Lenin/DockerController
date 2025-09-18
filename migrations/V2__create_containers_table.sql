CREATE TABLE IF NOT EXISTS repositories (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    url VARCHAR(255) NOT NULL,
    repositories_name VARCHAR(255) NOT NULL,
    description VARCHAR(255) NOT NULL
);