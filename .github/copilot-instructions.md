<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

## Telegram Currency Converter Bot Project

This project is a Python-based Telegram bot for currency conversion supporting:
- Traditional currencies: USD, EUR, RUB, UAH
- Cryptocurrencies: BTC, ETH, USDT, TRX, TON

### Project Structure
- `bot.py` - Main bot application
- `config.py` - Configuration and API keys
- `currency_api.py` - Currency conversion logic
- `requirements.txt` - Python dependencies
- `Dockerfile` - Container configuration
- `k8s/` - Kubernetes deployment manifests

### Development Guidelines
- Use async/await for Telegram bot operations
- Implement error handling for API calls
- Follow Python best practices and type hints
- Structure code for easy testing and deployment