# Используем базовый образ PostgreSQL
FROM postgres:latest

# Создаем директории pg_wal и archive и устанавливаем права доступа
RUN mkdir -p /oracle/pg_data/archive \
    && mkdir -p /var/lib/postgresql/data/pg_wal \
    && chown -R postgres:postgres /oracle/pg_data/archive \
    && chown -R postgres:postgres /var/lib/postgresql/data/pg_wal

# Копируем файл инициализации базы данных
COPY init.sql /docker-entrypoint-initdb.d/
RUN cat /docker-entrypoint-initdb.d/init.sql  # Вывод содержимого файла init.sql в консоль

# Устанавливаем метаданные для образа
LABEL name="db_image"
