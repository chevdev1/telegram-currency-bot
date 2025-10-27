#!/bin/bash
# Шпаргалка по управлению Telegram ботом

echo "=== УПРАВЛЕНИЕ TELEGRAM БОТОМ ==="

echo "1. ЗАПУСК БОТА:"
echo "cd /home/chv/Documents"
echo "source venv/bin/activate" 
echo "python bot.py"
echo ""

echo "2. ОСТАНОВКА БОТА:"
echo "Ctrl + C (в терминале с ботом)"
echo "или: pkill -f 'python bot.py'"
echo ""

echo "3. ЗАПУСК В ФОНЕ:"
echo "cd /home/chv/Documents"
echo "source venv/bin/activate"
echo "nohup python bot.py > bot_output.log 2>&1 &"
echo ""

echo "4. ПРОВЕРКА СТАТУСА:"
echo "ps aux | grep python"
echo ""

echo "5. ПРОСМОТР ЛОГОВ:"
echo "tail -f bot.log"
echo ""

echo "6. РЕСТАРТ БОТА:"
echo "pkill -f 'python bot.py'"
echo "cd /home/chv/Documents && source venv/bin/activate && python bot.py"
echo ""

echo "=== ПОЛЕЗНЫЕ КОМАНДЫ ==="
echo "docker images              # посмотреть Docker образы"
echo "docker ps                  # запущенные контейнеры"
echo "docker run currency-bot    # запустить бота в Docker"
echo ""