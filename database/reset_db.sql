\c postgres

SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = 'kbt'
  AND pid <> pg_backend_pid();

DROP DATABASE IF EXISTS kbt;
CREATE DATABASE kbt;

\c kbt

\i database/schema.sql

-- From project root
-- psql -h localhost -p 5433 -U postgres -f database/reset_db.sql

-- Connect to kbt
-- psql -h localhost -p 5433 -U postgres -d kbt -W


