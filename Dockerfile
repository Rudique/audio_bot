# Используем официальный Python 3.13 образ
FROM python:3.13-slim

# Устанавливаем ffmpeg и другие системные зависимости
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем requirements.txt
COPY requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект
COPY . .

# Создаем директорию для временных файлов
RUN mkdir -p temp

# Запускаем бота
CMD ["python", "bot.py"]
