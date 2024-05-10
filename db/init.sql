CREATE TABLE IF NOT EXISTS users_phone (
    user_id SERIAL PRIMARY KEY,
    phone_number VARCHAR(20) UNIQUE
);

CREATE TABLE IF NOT EXISTS users_emails (
    user_id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL
);
