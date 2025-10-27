"""
Модуль для работы с API валютных курсов
Здесь вся логика получения и конвертации валют
"""
import requests
import asyncio
from typing import Dict, Optional, Tuple
from loguru import logger
from config import Config

class CurrencyAPI:
    """
    Класс для работы с валютными API
    """
    
    def __init__(self):
        self.config = Config()
        # Кэш для курсов валют (чтобы не делать много запросов)
        self._cache: Dict[str, float] = {}
        self._cache_timeout = 300  # 5 минут
        
    async def get_exchange_rate(self, from_currency: str, to_currency: str) -> Optional[float]:
        """
        Получает курс обмена между двумя валютами
        
        Args:
            from_currency: Исходная валюта (например, 'USD')
            to_currency: Целевая валюта (например, 'RUB')
            
        Returns:
            float: Курс обмена или None если ошибка
        """
        try:
            # Проверяем, есть ли валюты в поддерживаемых
            if from_currency not in self.config.SUPPORTED_CURRENCIES:
                logger.warning(f"Неподдерживаемая валюта: {from_currency}")
                return None
                
            if to_currency not in self.config.SUPPORTED_CURRENCIES:
                logger.warning(f"Неподдерживаемая валюта: {to_currency}")
                return None
            
            # Если одинаковые валюты - курс 1:1
            if from_currency == to_currency:
                return 1.0
            
            # Получаем курсы для криптовалют и обычных валют по-разному
            if self._is_crypto(from_currency) or self._is_crypto(to_currency):
                return await self._get_crypto_rate(from_currency, to_currency)
            else:
                return await self._get_fiat_rate(from_currency, to_currency)
                
        except Exception as e:
            logger.error(f"Ошибка получения курса {from_currency}->{to_currency}: {e}")
            return None
    
    def _is_crypto(self, currency: str) -> bool:
        """Проверяет, является ли валюта криптовалютой"""
        return currency in self.config.CRYPTO_MAPPING
    
    async def _get_fiat_rate(self, from_currency: str, to_currency: str) -> Optional[float]:
        """
        Получает курс между обычными валютами (USD, EUR, RUB)
        """
        try:
            # Используем бесплатный API exchangerate-api.com
            url = f"{self.config.EXCHANGE_API_URL}/{from_currency}"
            
            # Делаем HTTP запрос
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Извлекаем курс для нужной валюты
            if to_currency in data.get('rates', {}):
                rate = data['rates'][to_currency]
                logger.info(f"Получен курс {from_currency}->{to_currency}: {rate}")
                return float(rate)
            else:
                logger.warning(f"Курс для {to_currency} не найден")
                return None
                
        except requests.RequestException as e:
            logger.error(f"Ошибка HTTP запроса: {e}")
            return None
        except KeyError as e:
            logger.error(f"Ошибка парсинга ответа API: {e}")
            return None
    
    async def _get_crypto_rate(self, from_currency: str, to_currency: str) -> Optional[float]:
        """
        Получает курс с участием криптовалют
        """
        try:
            # Если обе валюты крипто - пока не поддерживаем
            if self._is_crypto(from_currency) and self._is_crypto(to_currency):
                # Конвертируем через USD: crypto1 -> USD -> crypto2
                crypto1_to_usd = await self._get_crypto_to_fiat_rate(from_currency, 'USD')
                usd_to_crypto2 = await self._get_fiat_to_crypto_rate('USD', to_currency)
                
                if crypto1_to_usd and usd_to_crypto2:
                    return crypto1_to_usd * usd_to_crypto2
                return None
            
            # Если исходная валюта - криптовалюта
            if self._is_crypto(from_currency):
                return await self._get_crypto_to_fiat_rate(from_currency, to_currency)
            
            # Если целевая валюта - криптовалюта  
            if self._is_crypto(to_currency):
                return await self._get_fiat_to_crypto_rate(from_currency, to_currency)
                
        except Exception as e:
            logger.error(f"Ошибка получения крипто курса: {e}")
            return None
    
    async def _get_crypto_to_fiat_rate(self, crypto: str, fiat: str) -> Optional[float]:
        """Получает курс криптовалюты к обычной валюте"""
        try:
            crypto_id = self.config.CRYPTO_MAPPING.get(crypto)
            if not crypto_id:
                return None
            
            # Используем бесплатный API CoinGecko
            url = f"{self.config.CRYPTO_API_URL}"
            params = {
                'ids': crypto_id,
                'vs_currencies': fiat.lower()
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if crypto_id in data and fiat.lower() in data[crypto_id]:
                rate = data[crypto_id][fiat.lower()]
                logger.info(f"Получен крипто курс {crypto}->{fiat}: {rate}")
                return float(rate)
                
            return None
            
        except Exception as e:
            logger.error(f"Ошибка получения крипто курса {crypto}->{fiat}: {e}")
            return None
    
    async def _get_fiat_to_crypto_rate(self, fiat: str, crypto: str) -> Optional[float]:
        """Получает курс обычной валюты к криптовалюте"""
        # Получаем курс крипто к фиату и берем обратный
        crypto_to_fiat = await self._get_crypto_to_fiat_rate(crypto, fiat)
        if crypto_to_fiat and crypto_to_fiat > 0:
            return 1.0 / crypto_to_fiat
        return None
    
    async def convert_currency(self, amount: float, from_currency: str, to_currency: str) -> Optional[Tuple[float, float]]:
        """
        Конвертирует сумму из одной валюты в другую
        
        Args:
            amount: Сумма для конвертации
            from_currency: Исходная валюта
            to_currency: Целевая валюта
            
        Returns:
            Tuple[float, float]: (конвертированная_сумма, курс_обмена) или None
        """
        rate = await self.get_exchange_rate(from_currency, to_currency)
        if rate is not None:
            converted_amount = amount * rate
            return converted_amount, rate
        return None
    
    async def get_popular_rates(self) -> Dict[str, float]:
        """
        Получает курсы популярных валют к рублю
        """
        rates = {}
        base_currencies = ['USD', 'EUR', 'UAH', 'BTC', 'ETH', 'TRX', 'TON']
        
        for currency in base_currencies:
            rate = await self.get_exchange_rate(currency, 'RUB')
            if rate:
                rates[currency] = rate
                
        return rates