import asyncio
import os
from telethon import events
from rewriter import rewrite_text
from channel_manager import (
    get_active_target_peer_ids, get_all_channels,
    get_setting, set_setting, get_bool_setting, get_int_setting,
    add_channel, remove_channel, toggle_channel_status
)
from filters import (
    should_process_post,
    add_whitelist_keyword, add_blacklist_keyword,
    remove_whitelist_keyword, remove_blacklist_keyword,
    get_whitelist, get_blacklist,
    clear_whitelist, clear_blacklist
)
from config import DEST_CHANNEL

dest_entity = None
dest_peer_id = None
my_id = None

async def init_handlers(client):
    global dest_entity, dest_peer_id, my_id
    me = await client.get_me()
    my_id = me.id
    dest_entity = await client.get_entity(DEST_CHANNEL)
    dest_peer_id = dest_entity.id
    print(f"📡 Целевой канал: {DEST_CHANNEL} (ID: {dest_peer_id})")

# ==================== ОСНОВНОЙ ХЕНДЛЕР НОВОСТЕЙ ====================
@events.register(events.NewMessage)
async def news_handler(event):
    if event.out or event.chat_id == dest_peer_id:
        return

    if event.chat_id not in get_active_target_peer_ids():
        return

    original_text = event.message.message or ""
    
    if not should_process_post(original_text):
        return

    rewrite_enabled = get_bool_setting("rewrite_enabled")

    if rewrite_enabled:
        base_text = await rewrite_text(original_text)
    else:
        base_text = original_text or "Новость без текста"

    header = get_setting("post_header").strip()
    footer = get_setting("post_footer").strip()

    caption = base_text
    if header:
        caption = f"{header}\n\n{caption}"
    if footer:
        caption = f"{caption}\n\n{footer}"

    try:
        if event.message.media:
            media_path = await event.message.download_media()
            await event.client.send_file(
                entity=dest_entity,
                file=media_path,
                caption=caption,
                parse_mode="html"
            )
            if media_path and os.path.exists(media_path):
                os.remove(media_path)
        else:
            await event.client.send_message(dest_entity, caption, parse_mode="html")

        print(f"✅ Опубликовано из {get_all_channels().get(event.chat_id, {}).get('title', 'Неизвестный канал')}")

        delay = get_int_setting("post_delay_seconds", 15)
        await asyncio.sleep(delay)

    except Exception as e:
        print(f"❌ Ошибка публикации: {e}")

# ==================== ДАШБОРД ====================
@events.register(events.NewMessage(pattern=r"^/(.*)"))
async def dashboard_handler(event):
    if not event.is_private or event.sender_id != my_id:
        return

    text = event.message.message.strip()
    parts = text.split(maxsplit=1)
    command = parts[0].lower()
    arg = parts[1].strip() if len(parts) > 1 else ""

    if command == "/help":
        help_text = (
            "🛠 **Telegram Dashboard**\n\n"
            "Основные команды:\n"
            "/add @username — добавить канал\n"
            "/remove @username или ID — удалить\n"
            "/pause @username или ID — приостановить\n"
            "/resume @username или ID — возобновить\n"
            "/list — список каналов\n"
            "/settings — текущие настройки\n\n"
            "Фильтры:\n"
            "/addwhite слово — whitelist\n"
            "/addblack слово — blacklist\n"
            "/remwhite слово — удалить из white\n"
            "/remblack слово — удалить из black\n"
            "/whitelist — показать white\n"
            "/blacklist — показать black\n"
            "/clearwhite — очистить white\n"
            "/clearblack — очистить black\n\n"
            "Дополнительно:\n"
            "/setheader Текст... — заголовок\n"
            "/setfooter Текст... — футер\n"
            "/setdelay 15 — задержка (сек)\n"
            "/toggle rewrite — вкл/выкл рерайт\n"
            "/help — эта справка"
        )
        await event.reply(help_text)

    elif command == "/add" and arg:
        result = await add_channel(event.client, arg)
        await event.reply(result)
    elif command == "/remove" and arg:
        result = await remove_channel(event.client, arg)
        await event.reply(result)
    elif command == "/pause" and arg:
        result = await toggle_channel_status(event.client, arg, enable=False)
        await event.reply(result)
    elif command == "/resume" and arg:
        result = await toggle_channel_status(event.client, arg, enable=True)
        await event.reply(result)
    elif command == "/list":
        channels = get_all_channels()
        if not channels:
            await event.reply("📭 Список каналов пуст")
            return
        msg = "📋 **Целевые каналы:**\n\n"
        for pid, data in channels.items():
            status = "✅ Активен" if data["enabled"] else "⏸️ Приостановлен"
            msg += f"• {status} {data['title']} (@{data['username'] or '—'}) — ID: {pid}\n"
        await event.reply(msg)

    elif command == "/setheader":
        set_setting("post_header", arg)
        await event.reply(f"✅ **Заголовок** установлен:\n{arg or '— (пустой)'}")
    elif command == "/setfooter":
        set_setting("post_footer", arg)
        await event.reply(f"✅ **Футер** установлен:\n{arg or '— (пустой)'}")
    elif command == "/setdelay" and arg.isdigit():
        set_setting("post_delay_seconds", arg)
        await event.reply(f"✅ Задержка: **{arg} секунд**")
    elif command == "/toggle" and arg == "rewrite":
        current = get_bool_setting("rewrite_enabled")
        new_val = not current
        set_setting("rewrite_enabled", str(new_val))
        status = "✅ **ВКЛЮЧЁН**" if new_val else "❌ **ВЫКЛЮЧЕН**"
        await event.reply(f"🔄 Рерайт через GPT: {status}")

    elif command == "/addwhite" and arg:
        result = add_whitelist_keyword(arg)
        await event.reply(result)
    elif command == "/addblack" and arg:
        result = add_blacklist_keyword(arg)
        await event.reply(result)
    elif command == "/remwhite" and arg:
        result = remove_whitelist_keyword(arg)
        await event.reply(result)
    elif command == "/remblack" and arg:
        result = remove_blacklist_keyword(arg)
        await event.reply(result)
    elif command == "/whitelist":
        words = get_whitelist()
        await event.reply("📝 **Whitelist**:\n" + ("\n".join(f"• {w}" for w in words) if words else "— пусто"))
    elif command == "/blacklist":
        words = get_blacklist()
        await event.reply("📝 **Blacklist**:\n" + ("\n".join(f"• {w}" for w in words) if words else "— пусто"))
    elif command == "/clearwhite":
        clear_whitelist()
        await event.reply("🗑️ Whitelist полностью очищен")
    elif command == "/clearblack":
        clear_blacklist()
        await event.reply("🗑️ Blacklist полностью очищен")

    elif command in ("/status", "/settings"):
        rewrite = "✅ ВКЛЮЧЁН" if get_bool_setting("rewrite_enabled") else "❌ ВЫКЛЮЧЕН"
        delay = get_int_setting("post_delay_seconds", 15)
        header = get_setting("post_header") or "— (пустой)"
        footer = get_setting("post_footer") or "— (пустой)"
        wl = get_whitelist()
        bl = get_blacklist()
        await event.reply(
            f"**Настройки бота**\n\n"
            f"Рерайт GPT: {rewrite}\n"
            f"Задержка между постами: {delay} сек\n"
            f"Заголовок: {header}\n"
            f"Футер: {footer}\n"
            f"Whitelist: {len(wl)} слов\n"
            f"Blacklist: {len(bl)} слов\n"
            f"Целевой канал: {DEST_CHANNEL}"
        )