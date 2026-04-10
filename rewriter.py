from openai import AsyncOpenAI
from config import OPENAI_API_KEY

client = AsyncOpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = """
Ты — профессиональный рерайтер новостей для Telegram-канала.
Перепиши новость так, чтобы она была:
• 100% уникальной
• Живой, увлекательной и легко читаемой
• С новым ярким заголовком (можно с эмодзи)
• Короткие абзацы, отличная структура
• С сохранением ВСЕХ фактов и цифр
• Без воды и без упоминания источника

Отвечай ТОЛЬКО готовым текстом для публикации. Никаких пояснений.
"""

async def rewrite_text(original_text: str) -> str:
    if not original_text.strip():
        return "Новость без текста."
    try:
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Перепиши:\n\n{original_text}"}
            ],
            temperature=0.7,
            max_tokens=1500
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"❌ GPT ошибка: {e}")
        return original_text