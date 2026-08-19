-- Dữ liệu lab — không chứa PII thật
CREATE TABLE IF NOT EXISTS records (
    id   SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    value TEXT NOT NULL
);

INSERT INTO records (name, value) VALUES
    ('demo-1', 'alpha'),
    ('demo-2', 'beta'),
    ('demo-3', 'gamma');
