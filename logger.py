import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
from config import GOOGLE_SHEET_NAME, GOOGLE_SERVICE_ACCOUNT_JSON
import os

gc = None
sheet = None

def init_google_sheets():
    global gc, sheet
    if not os.path.exists(GOOGLE_SERVICE_ACCOUNT_JSON):
        print("❌ Файл credentials.json не найден!")
        return False
    
    try:
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        creds = Credentials.from_service_account_file(GOOGLE_SERVICE_ACCOUNT_JSON, scopes=scopes)
        gc = gspread.authorize(creds)
        sheet = gc.open(GOOGLE_SHEET_NAME).sheet1
        
        # Создаём заголовки, если таблица пустая
        if not sheet.get_all_values():
            sheet.append_row(["Дата", "Время", "Источник Канал", "Peer ID", "Оригинал", "Рерайт", "Статус"])
        print("✅ Google Sheets подключён успешно")
        return True
    except Exception as e:
        print(f"❌ Ошибка подключения к Google Sheets: {e}")
        return False

def log_publication(source_title: str, peer_id: int, original: str, rewritten: str, status: str = "Опубликовано"):
    if not sheet:
        return
    try:
        now = datetime.now()
        row = [
            now.strftime("%Y-%m-%d"),
            now.strftime("%H:%M:%S"),
            source_title,
            peer_id,
            original[:500] + "..." if len(original) > 500 else original,  # обрезаем для удобства
            rewritten[:500] + "..." if len(rewritten) > 500 else rewritten,
            status
        ]
        sheet.append_row(row)
    except Exception as e:
        print(f"❌ Ошибка записи в Google Sheets: {e}")