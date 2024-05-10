# Используем базовый образ Python
FROM python:3.8-slim

# Устанавливаем переменную окружения PYTHONUNBUFFERED для лучшей работы с выводом
ENV PYTHONUNBUFFERED 1

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файлы вашего бота и requirements.txt в контейнер
COPY bot.py requirements.txt /app/

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Команда для запуска вашего бота
CMD ["python", "bot.py"]

# Устанавливаем метаданные для образа
LABEL name="bot_image"
