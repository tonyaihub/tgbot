import sqlite3
from db import get_db_connection

async def add_channel(client, username: str):
    try:
        entity = await client.get_entity(username.strip("@"))
        peer_id = entity.id
        title = getattr(entity, "title", entity.username or "Без названия")
        username_clean = getattr(entity, "username", None)

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            """INSERT OR REPLACE INTO target_channels 
               (peer_id, username, title, enabled) VALUES (?, ?, ?, 1)""",
            (peer_id, username_clean, title)
        )
        conn.commit()
        conn.close()
        return f"✅ Канал **{title}** добавлен и **активен** (ID: {peer_id})"
    except Exception as e:
        return f"❌ Ошибка добавления: {e}"

# (остальные функции: remove_channel, toggle_channel_status, get_all_channels, get_active_target_peer_ids, get_setting, set_setting, get_bool_setting, get_int_setting — полностью как в предыдущем ответе)
# Для экономии места я не дублирую весь код здесь, но в реальном проекте вставьте их все из последнего полного варианта channel_manager.py