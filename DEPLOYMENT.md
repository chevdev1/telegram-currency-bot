# Telegram Currency Converter Bot - Deployment Guide

## 🎯 Bot Overview
- **9 currencies supported**: USD, EUR, RUB, UAH, BTC, ETH, USDT, TRX, TON
- **Interactive interface**: Inline keyboard buttons for easy navigation  
- **Manual input**: Users select currency pairs then enter custom amounts
- **Real-time rates**: Live currency and cryptocurrency conversion

## 🚀 Quick Start

### Local Development
```bash
# Clone and setup
git clone <repository>
cd telegram-currency-bot

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your BOT_TOKEN from @BotFather

# Run bot
python bot.py
```

### Docker Deployment
```bash
# Build image
docker build -t telegram-currency-bot .

# Run container
docker run --env-file .env telegram-currency-bot

# Or with environment variables
docker run -e BOT_TOKEN="your_token_here" telegram-currency-bot
```

### Kubernetes Deployment
```bash
# Apply secret (edit k8s/secret.yaml first)
kubectl apply -f k8s/secret.yaml

# Deploy bot
kubectl apply -f k8s/deployment.yaml

# Check status
kubectl get pods -l app=telegram-currency-bot
kubectl logs -l app=telegram-currency-bot
```

## 🎮 Bot Commands
- `/start` - Welcome message and instructions
- `/help` - Show available commands and usage examples
- `/rates` - Display current exchange rates
- `/convert` - Interactive currency conversion with buttons

## 🔧 User Experience Flow
1. User types `/convert`
2. Bot shows currency pair buttons (USDT→UAH, USD→UAH, etc.)
3. User selects a pair
4. Bot prompts for amount input with examples
5. User enters amount (e.g., "100", "50.5")
6. Bot shows conversion result with current rate

## 📊 Architecture
- **bot.py**: Main application with message handlers
- **config.py**: Currency definitions and bot configuration  
- **currency_api.py**: External API integration (ExchangeRate-API + CoinGecko)
- **Docker**: Containerized deployment with security best practices
- **Kubernetes**: Production-ready orchestration with secrets management

## 🔑 API Dependencies
- **Fiat currencies**: exchangerate-api.com (free tier)
- **Cryptocurrencies**: api.coingecko.com (free, no key required)

## 📈 Latest Updates
- ✅ Fixed all syntax errors and code structure
- ✅ Implemented interactive button interface
- ✅ Added manual amount input after currency selection
- ✅ Enhanced user experience with clear prompts and examples
- ✅ Docker image builds and runs successfully
- ✅ Ready for Kubernetes deployment

## 🛡️ Security Features
- Environment variables for sensitive data
- Non-root user in Docker container
- Kubernetes secrets for token management
- Input validation and error handling

Bot is now production-ready! 🎉