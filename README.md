# 🤖 Валютный Telegram Бот

<div align="center">
  <img src="assets/bot-icon.png" alt="Currency Bot Icon" width="200"/>
</div>

Telegram бот для конвертации валют с поддержкой криптовалют: USD, EUR, RUB, UAH, BTC, ETH, USDT, TRX, TON.

## 🚀 Быстрый старт


###  Локальный запуск

```bash
# Клонируйте проект
git clone <ваш-репозиторий>
cd currency-bot

# Создайте виртуальное окружение
python3 -m venv venv
source venv/bin/activate

# Установите зависимости
pip install -r requirements.txt

# Настройте токен
cp .env.example .env
# Отредактируйте .env и добавьте ваш BOT_TOKEN

# Запустите бота
python bot.py
```

###  Команды бота

- `/start` - Приветствие и справка
- `/help` - Помощь по командам  
- `/rates` - Актуальные курсы валют
- `/convert 100 USD to EUR` - Конвертация валют
- `50 USD` - Быстрая конвертация в рубли

###  Поддерживаемые валюты

- 🇺🇸 USD - Доллар США
- 🇪🇺 EUR - Евро
- 🇷🇺 RUB - Рубль
- 🇺🇦 UAH - Гривна
- ₿ BTC - Биткоин
- ⟠ ETH - Эфириум
- ₮ USDT - Tether
- � TRX - Tron
- �💎 TON - Toncoin

## 🐳 Docker развертывание

### Сборка образа

```bash
# Соберите Docker образ
docker build -t your-username/currency-bot:latest .

# Запустите локально (для тестирования)
docker run -e BOT_TOKEN=your_token your-username/currency-bot:latest

# Загрузите в Docker Hub
docker login
docker push your-username/currency-bot:latest
```

## ☸️ Kubernetes развертывание

### Подготовка кластера

```bash
# Запустите minikube (если используете)
minikube start

# Проверьте статус
kubectl cluster-info
```

### Развертывание бота

```bash
# Создайте namespace
kubectl apply -f k8s/namespace.yaml

# Настройте секреты (отредактируйте k8s/secret.yaml)
kubectl apply -f k8s/secret.yaml

# Разверните бота
kubectl apply -f k8s/deployment.yaml
```

### Управление

```bash
# Проверьте статус подов
kubectl get pods -n telegram-bots

# Посмотрите логи
kubectl logs -f deployment/currency-bot -n telegram-bots

# Масштабируйте (если нужно)
kubectl scale deployment currency-bot --replicas=2 -n telegram-bots

# Обновите образ
kubectl set image deployment/currency-bot currency-bot=your-username/currency-bot:v2 -n telegram-bots
```

## 📊 Мониторинг

```bash
# Статус всех ресурсов
kubectl get all -n telegram-bots

# Детальная информация о поде
kubectl describe pod <pod-name> -n telegram-bots

# События в namespace
kubectl get events -n telegram-bots
```

## 🔧 Разработка

### Структура проекта

```
├── bot.py              # Основной файл бота
├── config.py           # Конфигурация и настройки
├── currency_api.py     # Логика работы с API валют
├── requirements.txt    # Python зависимости
├── Dockerfile          # Конфигурация Docker
├── .dockerignore       # Исключения для Docker
├── .env.example        # Пример файла с переменными
├── assets/             # Ресурсы проекта
│   ├── bot-icon.svg    # Иконка бота (векторная)
│   └── bot-icon.png    # Иконка бота (для Telegram)
├── k8s/                # Kubernetes манифесты
│   ├── namespace.yaml
│   ├── secret.yaml
│   └── deployment.yaml
└── README.md           # Документация
```

### API для валютных курсов

Бот использует бесплатные API:
- **Обычные валюты**: [exchangerate-api.com](https://exchangerate-api.com/)
- **Криптовалюты**: [CoinGecko](https://coingecko.com/api)

### Логирование

Логи сохраняются в файл `bot.log` и выводятся в консоль.

## 🔐 Безопасность

- Никогда не коммитьте `.env` файл в git
- Используйте Kubernetes Secrets для токенов
- Запускайте контейнеры от непривилегированного пользователя
- Ограничивайте ресурсы контейнера

## 🆘 Устранение неполадок

### Бот не отвечает
```bash
# Проверьте логи
kubectl logs deployment/currency-bot -n telegram-bots

# Проверьте статус пода
kubectl describe pod <pod-name> -n telegram-bots
```

### Ошибки API
- Проверьте интернет соединение
- Убедитесь что API ключи корректны
- Проверьте лимиты запросов

### Проблемы с Docker
```bash
# Проверьте образ локально
docker run -it your-username/currency-bot:latest bash

# Проверьте переменные окружения
docker run your-username/currency-bot:latest env
```

## 📝 Лицензия

MIT License - используйте свободно для своих проектов!

## 🤝 Контрибуция

Создавайте issues и pull requests для улучшения бота!
