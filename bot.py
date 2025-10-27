"""
Основной файл Telegram бота для конвертации валют
Здесь вся логика обработки сообщений пользователей
"""
import asyncio
import re
from typing import Optional, Tuple
from telebot import TeleBot
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from loguru import logger

from config import Config
from currency_api import CurrencyAPI

class CurrencyBot:
    """
    Основной класс Telegram бота
    """
    
    def __init__(self):
        # Инициализируем конфигурацию и API
        self.config = Config()
        self.bot = TeleBot(self.config.BOT_TOKEN)
        self.currency_api = CurrencyAPI()
        
        # Настраиваем логирование
        logger.add("bot.log", rotation="1 MB", level="INFO")
        logger.info("Бот инициализирован")
        
        # Регистрируем обработчики сообщений
        self._register_handlers()
    
    def _create_conversion_keyboard(self) -> InlineKeyboardMarkup:
        """
        Создает клавиатуру с популярными конвертациями
        """
        keyboard = InlineKeyboardMarkup(row_width=2)
        
        # Первый ряд - USDT конвертации
        keyboard.row(
            InlineKeyboardButton("💰 USDT → UAH", callback_data="template_usdt_uah"),
            InlineKeyboardButton("💰 USDT → USD", callback_data="template_usdt_usd")
        )
        
        # Второй ряд - USD конвертации  
        keyboard.row(
            InlineKeyboardButton("💵 USD → UAH", callback_data="template_usd_uah"),
            InlineKeyboardButton("💵 USD → RUB", callback_data="template_usd_rub")
        )
        
        # Третий ряд - EUR конвертации
        keyboard.row(
            InlineKeyboardButton("💶 EUR → UAH", callback_data="template_eur_uah"),
            InlineKeyboardButton("💶 EUR → RUB", callback_data="template_eur_rub")
        )
        
        # Четвертый ряд - Криптовалюты
        keyboard.row(
            InlineKeyboardButton("₿ BTC → USD", callback_data="template_btc_usd"),
            InlineKeyboardButton("💎 TON → UAH", callback_data="template_ton_uah")
        )
        
        # Пятый ряд - TRX
        keyboard.row(
            InlineKeyboardButton("🔺 TRX → USD", callback_data="template_trx_usd"),
            InlineKeyboardButton("🔺 TRX → UAH", callback_data="template_trx_uah")
        )
        
        return keyboard
    
    def _register_handlers(self):
        """
        Регистрирует все обработчики команд и сообщений
        """
        
        @self.bot.message_handler(commands=['start'])
        def handle_start(message: Message):
            """Обработчик команды /start"""
            logger.info(f"Пользователь {message.from_user.id} запустил бота")
            
            # Отправляем приветствие с кнопками
            keyboard = self._create_conversion_keyboard()
            self.bot.reply_to(
                message, 
                self.config.MESSAGES['welcome'] + "\n💡 Выберите популярную конвертацию или используйте команды:",
                reply_markup=keyboard
            )
        
        @self.bot.message_handler(commands=['help'])
        def handle_help(message: Message):
            """Обработчик команды /help"""
            self.bot.reply_to(message, self.config.MESSAGES['help'])
        
        @self.bot.message_handler(commands=['rates'])
        def handle_rates(message: Message):
            """Обработчик команды /rates - показывает актуальные курсы"""
            logger.info(f"Пользователь {message.from_user.id} запросил курсы")
            
            # Запускаем асинхронную функцию в синхронном контексте
            rates = asyncio.run(self.currency_api.get_popular_rates())
            
            if rates:
                response = "💱 Актуальные курсы к рублю:\n\n"
                for currency, rate in rates.items():
                    currency_name = self.config.SUPPORTED_CURRENCIES.get(currency, currency)
                    response += f"{currency_name}: {rate:,.2f} ₽\n"
            else:
                response = "❌ Не удалось получить курсы валют"
            
            self.bot.reply_to(message, response)
        
        @self.bot.message_handler(commands=['convert'])
        def handle_convert_command(message: Message):
            """Обработчик команды /convert"""
            # Проверяем есть ли аргументы после команды
            text = message.text.strip()
            if len(text.split()) > 1:  # Если есть аргументы после /convert
                logger.info(f"Convert command with args: {text}")
                self._handle_convert(message, text)
            else:  # Если просто /convert без аргументов
                logger.info("Convert command without args - showing currency selection")
                self._send_currency_selection(message)
        
        @self.bot.message_handler(commands=['quick'])
        def handle_quick_convert(message: Message):
            """Обработчик команды /quick - показывает кнопки для быстрой конвертации"""
            keyboard = self._create_conversion_keyboard()
            self.bot.reply_to(
                message,
                "💱 Выберите валютную пару для быстрой конвертации:",
                reply_markup=keyboard
            )
        
        @self.bot.message_handler(func=lambda message: True)
        def handle_all_messages(message: Message):
            """Обработчик всех остальных сообщений"""
            text = message.text.strip()
            user_id = message.from_user.id
            
            # Проверяем, ждет ли пользователь ввод суммы после выбора валютной пары
            user_state = self._get_user_state(user_id)
            if user_state and user_state.get('waiting_for_amount'):
                self._handle_amount_input(message, user_state)
                return
            
            # Проверяем команду конвертации типа "/convert 100 usdt to uah"
            if text.lower().startswith('/convert '):
                self._handle_convert(message, text)
                return
            
            # Проверяем, не является ли это быстрой конвертацией (например: "100 USD")
            if self._is_quick_convert(text):
                self._handle_quick_convert(message, text)
            else:
                # Если не распознали формат - показываем справку с примерами
                help_text = """
❓ Не понял команду. Вот что можно делать:

📝 **Примеры команд:**
• `/convert 100 USDT to UAH`
• `/convert 50 USD to RUB` 
• `/convert 1000 RUB to UAH`
• `/convert 0.1 BTC to USD`

💡 **Или нажмите /convert для выбора валютной пары**
                """
                
                self.bot.reply_to(message, help_text)
        
        @self.bot.callback_query_handler(func=lambda call: True)
        def handle_callback_query(call: CallbackQuery):
            """Обработчик нажатий на inline кнопки"""
            try:
                data = call.data
                logger.info(f"Пользователь {call.from_user.id} нажал кнопку: {data}")
                
                if data.startswith("template_"):
                    # Обработка выбора валютной пары
                    self._handle_template_selection(call)
                elif data == "back_to_currencies":
                    # Возврат к выбору валютной пары
                    self._handle_back_to_currencies(call)
                    
                # Убираем "часики" с кнопки
                self.bot.answer_callback_query(call.id)
                
            except Exception as e:
                logger.error(f"Ошибка обработки callback: {e}")
                self.bot.answer_callback_query(call.id, "Произошла ошибка, попробуйте снова")
    
    def _handle_template_selection(self, call: CallbackQuery):
        """
        Обрабатывает выбор валютной пары и предлагает ввести сумму вручную
        """
        # Извлекаем валюты из callback_data
        template_parts = call.data.split("_")  # ['template', 'usdt', 'uah']
        from_currency = template_parts[1].upper()
        to_currency = template_parts[2].upper()
        
        # Получаем красивые названия валют
        currency_from_name = self.config.SUPPORTED_CURRENCIES.get(from_currency, from_currency)
        currency_to_name = self.config.SUPPORTED_CURRENCIES.get(to_currency, to_currency)
        
        # Создаем кнопку "Назад"
        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton("🔙 Выбрать другую пару", callback_data="back_to_currencies"))
        
        # Сохраняем выбранную пару в сообщении для последующей обработки
        new_text = f"💱 Выбрана пара: {currency_from_name} → {currency_to_name}\n\n"
        new_text += f"💰 Введите сумму в {from_currency}:\n\n"
        new_text += f"📝 Примеры:\n"
        
        # Добавляем примеры сумм в зависимости от валюты
        if from_currency == "USDT":
            new_text += "• 100 (для 100 USDT)\n• 50.5 (для 50.5 USDT)"
        elif from_currency == "USD":
            new_text += "• 100 (для 100 USD)\n• 25.75 (для 25.75 USD)"
        elif from_currency == "EUR":
            new_text += "• 50 (для 50 EUR)\n• 75.25 (для 75.25 EUR)"
        elif from_currency == "UAH":
            new_text += "• 1000 (для 1000 UAH)\n• 2500 (для 2500 UAH)"
        elif from_currency in ["BTC", "ETH"]:
            new_text += "• 0.1 (для 0.1 BTC)\n• 0.025 (для 0.025 BTC)"
        elif from_currency in ["TRX", "TON"]:
            new_text += "• 1000 (для 1000 TRX)\n• 5000 (для 5000 TRX)"
        else:
            new_text += "• 100 (для 100)\n• 50.5 (для 50.5)"
        
        new_text += f"\n\n⚡ Просто напишите число!"
        
        self.bot.edit_message_text(
            text=new_text,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=keyboard
        )
        
        # Сохраняем состояние пользователя (ждем ввод суммы)
        self._save_user_state(call.from_user.id, from_currency, to_currency)
    
    def _handle_back_to_currencies(self, call: CallbackQuery):
        """
        Возвращает пользователя к выбору валютных пар
        """
        # Очищаем состояние пользователя если есть
        if call.from_user.id in self._user_states:
            del self._user_states[call.from_user.id]
        
        # Показываем снова валютные пары
        self._send_currency_selection(call.message)
    
    def _send_currency_selection(self, message):
        """
        Отправляет пользователю выбор валютных пар
        """
        keyboard = InlineKeyboardMarkup()
        
        # Создаем популярные валютные пары
        currency_pairs = [
            ("USDT", "UAH", "💰 USDT → UAH"),
            ("USD", "UAH", "💵 USD → UAH"),
            ("EUR", "UAH", "💶 EUR → UAH"),
            ("RUB", "UAH", "₽ RUB → UAH"), 
            ("USDT", "USD", "💰 USDT → USD"),
            ("BTC", "USD", "₿ BTC → USD"),
            ("ETH", "USD", "⟠ ETH → USD"),
            ("TON", "USD", "💎 TON → USD"),
            ("TRX", "USD", "🔥 TRX → USD"),
            ("RUB", "USD", "₽ RUB → USD")
        ]
        
        # Добавляем кнопки для валютных пар
        for from_curr, to_curr, display_name in currency_pairs:
            callback_data = f"template_{from_curr.lower()}_{to_curr.lower()}"
            keyboard.row(InlineKeyboardButton(display_name, callback_data=callback_data))
        
        # Создаем или изменяем сообщение
        text = "💱 Выберите валютную пару для конвертации:\n\n"
        text += "📊 Доступны актуальные курсы валют и криптовалют\n"
        text += "⚡ После выбора введите сумму для конвертации"
        
        if hasattr(message, 'message_id'):  # Это callback query
            self.bot.edit_message_text(
                text=text,
                chat_id=message.chat.id,
                message_id=message.message_id,
                reply_markup=keyboard
            )
        else:  # Это обычное сообщение
            self.bot.send_message(
                chat_id=message.chat.id,
                text=text,
                reply_markup=keyboard
            )
    
    def _save_user_state(self, user_id: int, from_currency: str, to_currency: str):
        """
        Сохраняет состояние пользователя (какую валютную пару он выбрал)
        """
        # Используем простой словарь для хранения состояний
        if not hasattr(self, '_user_states'):
            self._user_states = {}
        
        self._user_states[user_id] = {
            'from_currency': from_currency,
            'to_currency': to_currency,
            'waiting_for_amount': True
        }
    
    def _get_user_state(self, user_id: int):
        """
        Получает состояние пользователя
        """
        if not hasattr(self, '_user_states'):
            return None
        return self._user_states.get(user_id)
    
    def _handle_amount_input(self, message: Message, user_state: dict):
        """
        Обрабатывает ввод суммы пользователем после выбора валютной пары
        """
        try:
            # Пробуем парсить введенную сумму
            amount_text = message.text.strip().replace(',', '.')
            amount = float(amount_text)
            
            if amount <= 0:
                self.bot.reply_to(message, "❌ Сумма должна быть больше нуля. Попробуйте еще раз:")
                return
            
            if amount > 1000000000:  # Лимит в миллиард
                self.bot.reply_to(message, "❌ Слишком большая сумма. Введите меньше:")
                return
            
            # Получаем валюты из состояния
            from_currency = user_state['from_currency']
            to_currency = user_state['to_currency']
            
            # Выполняем конвертацию
            self._perform_conversion(message, amount, from_currency, to_currency)
            
            # Очищаем состояние пользователя
            self._clear_user_state(message.from_user.id)
            
            # Предлагаем еще конвертацию
            keyboard = InlineKeyboardMarkup()
            keyboard.row(InlineKeyboardButton("🔄 Еще конвертация", callback_data="back_to_currencies"))
            self.bot.send_message(
                message.chat.id,
                "💡 Хотите выполнить еще одну конвертацию?",
                reply_markup=keyboard
            )
            
        except ValueError:
            # Если не удалось парсить число
            self.bot.reply_to(
                message, 
                "❌ Введите корректное число.\n\n📝 Примеры: 100, 50.5, 0.25\n\n💰 Попробуйте еще раз:"
            )
    
    def _clear_user_state(self, user_id: int):
        """
        Очищает состояние пользователя
        """
        if hasattr(self, '_user_states') and user_id in self._user_states:
            del self._user_states[user_id]
    
    def _handle_template_selection(self, call: CallbackQuery):
        """
        Обрабатывает выбор валютной пары и предлагает ввести сумму вручную
        """
        # Извлекаем валюты из callback_data
        template_parts = call.data.split("_")  # ['template', 'usdt', 'uah']
        from_currency = template_parts[1].upper()
        to_currency = template_parts[2].upper()
        
        # Получаем красивые названия валют
        currency_from_name = self.config.SUPPORTED_CURRENCIES.get(from_currency, from_currency)
        currency_to_name = self.config.SUPPORTED_CURRENCIES.get(to_currency, to_currency)
        
        # Создаем кнопку "Назад"
        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton("🔙 Выбрать другую пару", callback_data="back_to_currencies"))
        
        # Сохраняем выбранную пару в сообщении для последующей обработки
        new_text = f"💱 Выбрана пара: {currency_from_name} → {currency_to_name}\n\n"
        new_text += f"💰 Введите сумму в {from_currency}:\n\n"
        new_text += f"📝 Примеры:\n"
        
        # Добавляем примеры сумм в зависимости от валюты
        if from_currency == "USDT":
            new_text += "• 100 (для 100 USDT)\n• 50.5 (для 50.5 USDT)"
        elif from_currency == "USD":
            new_text += "• 100 (для 100 USD)\n• 25.75 (для 25.75 USD)"
        elif from_currency == "EUR":
            new_text += "• 50 (для 50 EUR)\n• 75.25 (для 75.25 EUR)"
        elif from_currency == "UAH":
            new_text += "• 1000 (для 1000 UAH)\n• 2500 (для 2500 UAH)"
        elif from_currency in ["BTC", "ETH"]:
            new_text += "• 0.1 (для 0.1 BTC)\n• 0.025 (для 0.025 BTC)"
        elif from_currency in ["TRX", "TON"]:
            new_text += "• 1000 (для 1000 TRX)\n• 5000 (для 5000 TRX)"
        else:
            new_text += "• 100 (для 100)\n• 50.5 (для 50.5)"
        
        new_text += f"\n\n⚡ Просто напишите число!"
        
        self.bot.edit_message_text(
            text=new_text,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=keyboard
        )
        
        # Сохраняем состояние пользователя (ждем ввод суммы)
        self._save_user_state(call.from_user.id, from_currency, to_currency)
    
    def _handle_back_to_currencies(self, call: CallbackQuery):
        """
        Возвращает к выбору валютной пары
        """
        keyboard = self._create_conversion_keyboard()
        new_text = "💱 Выберите валютную пару для быстрой конвертации:"
        
        # Очищаем состояние пользователя если есть
        self._clear_user_state(call.from_user.id)
        
        self.bot.edit_message_text(
            text=new_text,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=keyboard
        )
    
    def _is_quick_convert(self, text: str) -> bool:
        """
        Проверяет, является ли текст быстрой конвертацией
        """
        # Убрать эту функцию или добавить логику проверки
        return False
    
    def _handle_back_to_currencies(self, call: CallbackQuery):
        """
        Возвращает к выбору валютной пары
        """
        keyboard = self._create_conversion_keyboard()
        new_text = "💱 Выберите валютную пару для быстрой конвертации:"
        
        self.bot.edit_message_text(
            text=new_text,
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=keyboard
        )
    
    def _perform_conversion_callback(self, call: CallbackQuery, amount: float, from_currency: str, to_currency: str):
        """
        Выполняет конвертацию валют для callback запроса
        """
        try:
            logger.info(f"Callback конвертация: {amount} {from_currency} в {to_currency}")
            
            # Запускаем асинхронную конвертацию
            result = asyncio.run(self.currency_api.convert_currency(amount, from_currency, to_currency))
            
            if result:
                converted_amount, exchange_rate = result
                
                # Форматируем ответ
                from_name = self.config.SUPPORTED_CURRENCIES[from_currency]
                to_name = self.config.SUPPORTED_CURRENCIES[to_currency]
                
                response = f"💱 Конвертация выполнена!\n\n"
                response += f"📊 {amount:,.2f} {from_name}\n"
                response += f"🔄 {converted_amount:,.2f} {to_name}\n\n"
                response += f"📈 Курс: 1 {from_currency} = {exchange_rate:,.4f} {to_currency}\n\n"
                response += "💡 Хотите еще конвертацию? Нажмите /quick"
                
                # Создаем новую клавиатуру для повтора
                keyboard = InlineKeyboardMarkup()
                keyboard.row(InlineKeyboardButton("🔄 Еще конвертация", callback_data="back_to_currencies"))
                
                self.bot.edit_message_text(
                    text=response,
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    reply_markup=keyboard
                )
                
                logger.info(f"Успешная callback конвертация: {amount} {from_currency} = {converted_amount} {to_currency}")
                
            else:
                self.bot.edit_message_text(
                    text="❌ Не удалось получить курс валют. Попробуйте позже.",
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id
                )
                
        except Exception as e:
            logger.error(f"Ошибка callback конвертации: {e}")
            self.bot.edit_message_text(
                text="❌ Произошла ошибка при конвертации.",
                chat_id=call.message.chat.id,
                message_id=call.message.message_id
            )

    def _is_quick_convert(self, text: str) -> bool:
        """
        Проверяет, является ли сообщение быстрой конвертацией
        Примеры: "100 USD", "0.5 BTC", "50 EUR"
        """
        pattern = r'^\d+(?:\.\d+)?\s+[A-Z]{3,4}$'
        return bool(re.match(pattern, text.upper()))
    
    def _handle_quick_convert(self, message: Message, text: str):
        """
        Обрабатывает быструю конвертацию в рубли
        """
        try:
            parts = text.upper().split()
            amount = float(parts[0])
            from_currency = parts[1]
            
            # Конвертируем в рубли по умолчанию
            self._perform_conversion(message, amount, from_currency, self.config.DEFAULT_TARGET_CURRENCY)
            
        except (ValueError, IndexError) as e:
            logger.error(f"Ошибка парсинга быстрой конвертации: {e}")
            self.bot.reply_to(message, self.config.MESSAGES['invalid_format'])
    
    def _handle_convert(self, message: Message, text: str):
        """
        Обрабатывает команду конвертации
        Примеры: "/convert 100 USD to EUR", "/convert 0.5 BTC to RUB"
        """
        # Парсим команду конвертации
        parsed = self._parse_convert_command(text)
        
        if not parsed:
            self.bot.reply_to(message, self.config.MESSAGES['invalid_format'])
            return
        
        amount, from_currency, to_currency = parsed
        self._perform_conversion(message, amount, from_currency, to_currency)
    
    def _parse_convert_command(self, text: str) -> Optional[Tuple[float, str, str]]:
        """
        Парсит команду конвертации
        
        Returns:
            Tuple[float, str, str]: (сумма, исходная_валюта, целевая_валюта)
        """
        try:
            # Убираем /convert и разбиваем на части
            text = text.replace('/convert', '').strip()
            
            # Паттерн: "100 USD to EUR" (регистронезависимый)
            pattern = r'(\d+(?:\.\d+)?)\s+([a-zA-Z]{3,4})\s+(?:to|TO)\s+([a-zA-Z]{3,4})'
            match = re.match(pattern, text, re.IGNORECASE)
            
            if match:
                amount = float(match.group(1))
                from_currency = match.group(2).upper()
                to_currency = match.group(3).upper()
                
                logger.info(f"Parsed convert command: {amount} {from_currency} -> {to_currency}")
                return amount, from_currency, to_currency
            
            logger.warning(f"Failed to parse convert command: '{text}'")
            return None
            
        except (ValueError, AttributeError) as e:
            logger.error(f"Ошибка парсинга команды конвертации: {e}")
            return None
    
    def _perform_conversion(self, message: Message, amount: float, from_currency: str, to_currency: str):
        """
        Выполняет конвертацию валют и отправляет результат
        """
        try:
            # Проверяем поддержку валют
            if from_currency not in self.config.SUPPORTED_CURRENCIES:
                currencies = ', '.join(self.config.SUPPORTED_CURRENCIES.keys())
                error_msg = self.config.MESSAGES['unsupported_currency'].format(currencies=currencies)
                self.bot.reply_to(message, error_msg)
                return
            
            if to_currency not in self.config.SUPPORTED_CURRENCIES:
                currencies = ', '.join(self.config.SUPPORTED_CURRENCIES.keys())
                error_msg = self.config.MESSAGES['unsupported_currency'].format(currencies=currencies)
                self.bot.reply_to(message, error_msg)
                return
            
            # Выполняем конвертацию
            logger.info(f"Конвертируем {amount} {from_currency} в {to_currency}")
            
            # Запускаем асинхронную конвертацию
            result = asyncio.run(self.currency_api.convert_currency(amount, from_currency, to_currency))
            
            if result:
                converted_amount, exchange_rate = result
                
                # Форматируем ответ
                from_name = self.config.SUPPORTED_CURRENCIES[from_currency]
                to_name = self.config.SUPPORTED_CURRENCIES[to_currency]
                
                response = f"💱 Конвертация:\n\n"
                response += f"📊 {amount:,.2f} {from_name}\n"
                response += f"🔄 {converted_amount:,.2f} {to_name}\n\n"
                response += f"📈 Курс: 1 {from_currency} = {exchange_rate:,.4f} {to_currency}"
                
                self.bot.reply_to(message, response)
                
                logger.info(f"Успешная конвертация: {amount} {from_currency} = {converted_amount} {to_currency}")
                
            else:
                self.bot.reply_to(message, self.config.MESSAGES['error'])
                logger.error(f"Не удалось получить курс {from_currency} -> {to_currency}")
                
        except Exception as e:
            logger.error(f"Ошибка выполнения конвертации: {e}")
            self.bot.reply_to(message, self.config.MESSAGES['error'])
    
    def run(self):
        """
        Запускает бота
        """
        logger.info("Запускаем бота...")
        try:
            # Проверяем токен
            if not self.config.BOT_TOKEN:
                logger.error("BOT_TOKEN не задан! Создайте файл .env с токеном.")
                return
            
            # Запускаем polling (постоянное получение сообщений)
            logger.info("Бот запущен и готов к работе!")
            self.bot.infinity_polling(timeout=10, long_polling_timeout=5)
            
        except Exception as e:
            logger.error(f"Ошибка запуска бота: {e}")
            raise

def main():
    """
    Точка входа в приложение
    """
    try:
        # Создаем и запускаем бота
        bot = CurrencyBot()
        bot.run()
        
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
        raise

if __name__ == "__main__":
    main()