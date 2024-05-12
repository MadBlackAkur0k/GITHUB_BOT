-- Установка активной базы данных на db_tg_bot
\c db_tg_bot;

-- Создание пользователя repl_user для репликации
CREATE USER repl_user WITH REPLICATION PASSWORD 'Qq12345';

-- Создание таблицы users_phone
CREATE TABLE users_phone (
    user_id SERIAL PRIMARY KEY,
    phone_number VARCHAR(20) UNIQUE
);

-- Создание таблицы users_emails
CREATE TABLE  users_emails (
    user_id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL
);

-- Даем пользователям postgres и repl_user права на созданные таблицы
GRANT ALL PRIVILEGES ON TABLE users_phone TO postgres, repl_user;
GRANT ALL PRIVILEGES ON TABLE users_emails TO postgres, repl_user;


SELECT * FROM pg_create_physical_replication_slot('replication_slot');
