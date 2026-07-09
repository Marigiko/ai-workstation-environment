#!/usr/bin/env python3
"""Test Telegram bot connection."""

import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Load .env if exists
env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(env_path)

async def test_connection():
    """Test bot connection to Telegram."""
    from telegram import Bot

    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("❌ TELEGRAM_BOT_TOKEN not set")
        print("")
        print("Set it with:")
        print("  export TELEGRAM_BOT_TOKEN='your_token'")
        print("")
        print("Or run: ./setup.sh")
        return False

    try:
        bot = Bot(token=token)
        me = await bot.get_me()
        print("✅ Conexión exitosa!")
        print(f"   Bot: @{me.username}")
        print(f"   Nombre: {me.first_name}")
        print(f"   ID: {me.id}")
        print("")
        print("📱 Busca tu bot en Telegram y envía /start")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        print("")
        print("Verifica que el token sea válido.")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_connection())
    exit(0 if success else 1)
