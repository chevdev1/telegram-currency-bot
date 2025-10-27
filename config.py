"""
Конфигурационный файл бота
Здесь хранятся все настройки, токены и константы
"""
import os
from typing import Dict, List
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()

class Config:
    """
    Класс для хранения всех настроек бота
    """
    # Токен Telegram бота (получаем из переменной окружения для безопасности)
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    
    # API ключ для получения курсов валют (бесплатный сервис)
    # Регистрируетесь на https://exchangerate-api.com/ для получения ключа
    EXCHANGE_API_KEY = os.getenv('EXCHANGE_API_KEY', 'demo_key')
    
    # Поддерживаемые валюты
    SUPPORTED_CURRENCIES: Dict[str, str] = {
        'USD': '🇺🇸 Доллар США',
        'EUR': '🇪🇺 Евро', 
        'RUB': '🇷🇺 Рубль',
        'UAH': '🇺🇦 Гривна',
        'BTC': '₿ Биткоин',
        'ETH': '⟠ Эфириум',
        'USDT': '₮ Tether',
        'TRX': '🔺 Tron',
        'TON': '💎 Toncoin'
    }
    
    # Валюта по умолчанию для конвертации
    DEFAULT_TARGET_CURRENCY = 'RUB'
    
    # URL для API курсов (бесплатный сервис)
    EXCHANGE_API_URL = 'https://api.exchangerate-api.com/v4/latest'
    
    # URL для криптовалют (бесплатный API CoinGecko)
    CRYPTO_API_URL = 'https://api.coingecko.com/api/v3/simple/price'
    
    # Маппинг криптовалют для API
    CRYPTO_MAPPING: Dict[str, str] = {
        'BTC': 'bitcoin',
        'ETH': 'ethereum', 
        'USDT': 'tether',
        'TRX': 'tron',
        'TON': 'the-open-network'
    }
    
    # Сообщения бота
    MESSAGES = {
        'welcome': """
🤖 Привет! Я валютный конвертер бот!

💱 Что я умею:
• Конвертировать валюты: `/convert 100 USD to EUR`
• Показывать курсы: `/rates`
• Быстрая конвертация: просто напишите `20 USD`

💰 Поддерживаемые валюты: USD, EUR, RUB, UAH, BTC, ETH, USDT, TRX, TON

Попробуйте прямо сейчас! 🚀
        """,
        
        'help': """
📖 Справка по командам:

/start - Показать приветствие с кнопками
/quick - Быстрая конвертация (кнопки)
/help - Эта справка  
/rates - Актуальные курсы валют
/convert <сумма> <валюта> to <валюта> - Конвертация

📝 Примеры:
• `/convert 100 USD to RUB`
• `/convert 50 EUR to UAH`
• `/convert 0.5 BTC to USD`
• `/convert 1000 TRX to USD`
• `/convert 1000 UAH to EUR`
• `50 EUR` (быстрая конвертация в рубли)

💡 Самый удобный способ - команда /quick!
        """,
        
        'error': '❌ Произошла ошибка. Попробуйте позже.',
        'invalid_format': '❌ Неверный формат. Используйте: `/convert 100 USD to EUR`',
        'unsupported_currency': '❌ Валюта не поддерживается. Доступны: {currencies}'
    }