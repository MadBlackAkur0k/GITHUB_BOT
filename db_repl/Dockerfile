# Используем официальный образ PostgreSQL в качестве базового
FROM postgres:latest

# Устанавливаем метаданные для образа
LABEL name="db_repl_image"

# Создаем каталог для запуска PostgreSQL и назначаем права
RUN mkdir -p /var/run/postgresql && chown -R postgres:postgres /var/run/postgresql

# Переключаемся на пользователя postgres
USER postgres
