# Используем базовый образ PostgreSQL
FROM postgres:latest

# Устанавливаем переменную окружения для пароля PostgreSQL
ENV POSTGRES_PASSWORD=Qq12345

# Копируем файл инициализации базы данных
COPY init.sql /docker-entrypoint-initdb.d/

# Создаем директории и устанавливаем права доступа
RUN mkdir -p /oracle/pg_data/archive/ && \
    chown -R postgres:postgres /oracle/pg_data/archive/ && \
    chmod 700 /oracle/pg_data/archive/ && \
    chown -R postgres:postgres /var/lib/postgresql/data && \
    chmod 700 /var/lib/postgresql/data

# Устанавливаем таймзону Europe/Moscow
RUN ln -fs /usr/share/zoneinfo/Europe/Moscow /etc/localtime

# Устанавливаем пользователя postgres
USER postgres

# Команда для запуска PostgreSQL
CMD ["pg_ctl -D /var/lib/postgresql/data -l logfile start"]
