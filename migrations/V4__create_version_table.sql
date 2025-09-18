CREATE TABLE IF NOT EXISTS containers (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    containers_name VARCHAR(255) NOT NULL,
    repositories_id INTEGER NOT NULL,
    version VARCHAR(255) NOT NULL
);