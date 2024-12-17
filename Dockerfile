# Используем официальный образ Python
FROM python:3.10-slim

# Устанавливаем рабочую директорию внутри контейнера

# Копируем файл зависимостей (requirements.txt) и устанавливаем их
COPY requirements.txt .
COPY main.py .
COPY .env .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем все файлы приложения в контейнер


# Команда запуска приложения
#CMD ["uvicorn", "main1:app", "--host", "0.0.0.0", "--port", "9500"]