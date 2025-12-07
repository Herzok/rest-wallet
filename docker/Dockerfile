# Используем официальный образ Python
FROM python:latest

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Устанавливаем пакеты
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Открываем порт для Django
EXPOSE 8000

# Команда для старта Django приложения
#CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
#команда чтобы контейнер «висел» в активном состоянии 
CMD ["tail", "-f", "/dev/null"]