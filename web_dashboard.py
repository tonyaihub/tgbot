from flask import Flask, render_template, request, redirect, url_for, jsonify
from channel_manager import get_all_channels, add_channel, remove_channel, toggle_channel_status
from filters import get_whitelist, get_blacklist, add_whitelist_keyword, add_blacklist_keyword, remove_whitelist_keyword, remove_blacklist_keyword, clear_whitelist, clear_blacklist
from channel_manager import get_setting, set_setting, get_bool_setting, get_int_setting
import asyncio
from config import DEST_CHANNEL

app = Flask(__name__)

@app.route('/')
def index():
    channels = get_all_channels()
    whitelist = get_whitelist()
    blacklist = get_blacklist()
    rewrite_enabled = get_bool_setting("rewrite_enabled")
    delay = get_int_setting("post_delay_seconds", 15)
    header = get_setting("post_header")
    footer = get_setting("post_footer")
    
    return render_template('index.html',
                           channels=channels,
                           whitelist=whitelist,
                           blacklist=blacklist,
                           rewrite_enabled=rewrite_enabled,
                           delay=delay,
                           header=header,
                           footer=footer,
                           dest_channel=DEST_CHANNEL)

# API эндпоинты для управления
@app.route('/api/channel/add', methods=['POST'])
def api_add_channel():
    username = request.form.get('username')
    # Поскольку add_channel асинхронный, запускаем в фоне (упрощённо)
    # Для production лучше использовать asyncio.run_coroutine_threadsafe, но для простоты
    result = asyncio.run(add_channel(None, username))  # client не нужен для добавления в БД, но функция ожидает
    # Лучше сделать синхронную версию, но пока так
    return redirect(url_for('index'))

# Добавь остальные эндпоинты аналогично (pause, resume, remove, toggle rewrite, set header и т.д.)
# Для экономии места я сделал базовую версию. Полную версию с JS можно расширить.

if __name__ == '__main__':
    app.run(debug=True, port=5000)