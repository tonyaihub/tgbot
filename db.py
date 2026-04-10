import sqlite3
from pathlib import Path

DB_PATH = Path("bot_data.db")

def init_db():
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS target_channels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            peer_id INTEGER UNIQUE NOT NULL,
            username TEXT,
            title TEXT,
            enabled INTEGER DEFAULT 1
        )
    ''')
    
    cur.execute("PRAGMA table_info(target_channels)")
    columns = [info[1] for info in cur.fetchall()]
    if "enabled" not in columns:
        cur.execute("ALTER TABLE target_channels ADD COLUMN enabled INTEGER DEFAULT 1")
        cur.execute("UPDATE target_channels SET enabled = 1 WHERE enabled IS NULL")
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS whitelist_keywords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            keyword TEXT UNIQUE NOT NULL
        )
    ''')
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS blacklist_keywords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            keyword TEXT UNIQUE NOT NULL
        )
    ''')
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    ''')
    
    defaults = {
        "rewrite_enabled": "true",
        "post_delay_seconds": "15",
        "post_header": "",
        "post_footer": ""
    }
    for key, value in defaults.items():
        cur.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (key, value))
    
    conn.commit()
    conn.close()

def get_db_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)