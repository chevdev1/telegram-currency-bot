# Используем официальный Python образ
FROM python:3.11-slim

# Создаем пользователя без root прав (безопасность)
RUN useradd --create-home --shell /bin/bash botuser

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файл зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY bot.py .
COPY config.py .
COPY currency_api.py .

# Меняем владельца файлов на botuser
RUN chown -R botuser:botuser /app

# Переключаемся на непривилегированного пользователя
USER botuser

# Указываем команду запуска
CMD ["python", "bot.py"]