CREATE TABLE IF NOT EXISTS version (
    id SERIAL PRIMARY KEY,
    repositories_id INTEGER NOT NULL,
    version VARCHAR(255) NOT NULL
);