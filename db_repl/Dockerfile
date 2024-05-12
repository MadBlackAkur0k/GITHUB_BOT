# Используем базовый образ PostgreSQL
FROM postgres:13

# Устанавливаем переменную окружения для пароля PostgreSQL
ENV POSTGRES_PASSWORD=Qq12345

# Устанавливаем необходимые пакеты
RUN apt-get update && apt-get install -y net-tools procps postgresql-client

# Задаем команду по умолчанию
CMD ["bash"]

# Устанавливаем метаданные для образа
LABEL name="db_repl_image"
