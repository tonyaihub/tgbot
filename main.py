import asyncio
import threading
from telethon import TelegramClient
from config import API_ID, API_HASH, PHONE
from db import init_db
from handlers import init_handlers, news_handler, dashboard_handler
from logger import init_google_sheets
from web_dashboard import app as flask_app

client = TelegramClient("session/news_parser", API_ID, API_HASH)

def run_flask():
    flask_app.run(host='0.0.0.0', port=5000, debug=False)

async def main():
    init_db()
    init_google_sheets()
    
    print("🚀 Запуск бота...")
    await client.start(phone=PHONE)
    await init_handlers(client)
    
    client.add_event_handler(news_handler)
    client.add_event_handler(dashboard_handler)
    
    print("✅ Telethon бот запущен")
    print("🌐 Веб-панель: http://127.0.0.1:5000")
    print("📲 Telegram дашборд: /help в Избранное")
    
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())