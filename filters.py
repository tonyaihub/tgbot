from db import get_db_connection

def add_whitelist_keyword(keyword: str) -> str:
    keyword = keyword.strip().lower()
    if not keyword:
        return "❌ Ключевое слово не может быть пустым"
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO whitelist_keywords (keyword) VALUES (?)", (keyword,))
        conn.commit()
        conn.close()
        return f"✅ Добавлено в whitelist: **{keyword}**"
    except sqlite3.IntegrityError:
        return f"⚠️ Слово **{keyword}** уже есть в whitelist"
    except Exception as e:
        return f"❌ Ошибка: {e}"

def add_blacklist_keyword(keyword: str) -> str:
    keyword = keyword.strip().lower()
    if not keyword:
        return "❌ Ключевое слово не может быть пустым"
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO blacklist_keywords (keyword) VALUES (?)", (keyword,))
        conn.commit()
        conn.close()
        return f"✅ Добавлено в blacklist: **{keyword}**"
    except sqlite3.IntegrityError:
        return f"⚠️ Слово **{keyword}** уже есть в blacklist"
    except Exception as e:
        return f"❌ Ошибка: {e}"

def remove_whitelist_keyword(keyword: str) -> str:
    keyword = keyword.strip().lower()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM whitelist_keywords WHERE keyword = ?", (keyword,))
    deleted = cur.rowcount
    conn.commit()
    conn.close()
    return f"🗑️ Удалено из whitelist: **{keyword}**" if deleted else f"❌ Слово **{keyword}** не найдено в whitelist"

def remove_blacklist_keyword(keyword: str) -> str:
    keyword = keyword.strip().lower()
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM blacklist_keywords WHERE keyword = ?", (keyword,))
    deleted = cur.rowcount
    conn.commit()
    conn.close()
    return f"🗑️ Удалено из blacklist: **{keyword}**" if deleted else f"❌ Слово **{keyword}** не найдено в blacklist"

def get_whitelist() -> list:
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT keyword FROM whitelist_keywords")
    return [row[0] for row in cur.fetchall()]

def get_blacklist() -> list:
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT keyword FROM blacklist_keywords")
    return [row[0] for row in cur.fetchall()]

def clear_whitelist():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM whitelist_keywords")
    conn.commit()
    conn.close()

def clear_blacklist():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM blacklist_keywords")
    conn.commit()
    conn.close()

def should_process_post(text: str) -> bool:
    if not text:
        return False
    text_lower = text.lower()
    
    whitelist = get_whitelist()
    blacklist = get_blacklist()
    
    if whitelist:
        if not any(kw in text_lower for kw in whitelist):
            return False
    
    if any(kw in text_lower for kw in blacklist):
        return False
    
    return True