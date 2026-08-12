import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not BOT_TOKEN:
    raise ValueError("No TELEGRAM_TOKEN found")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- ОБРАБОТЧИК ЗАЯВОК НА ВСТУПЛЕНИЕ ---
@dp.chat_join_request()
async def handle_join_request(update: types.ChatJoinRequest):
    user_id = update.from_user.id
    user_name = update.from_user.first_name
    
    # 1. СНАЧАЛА отправляем сообщение (БЕЗ ЗАДЕРЖЕК!)
    try:
        await bot.send_message(
            chat_id=user_id,
            text=(
                f"Привет, {user_name}! 👋\n\n"
                "Добро пожаловать в закрытый канал с акциями!\n"
                "Твой запрос на вступление одобрен. 🎉\n\n"
                "Теперь ты будешь первым узнавать о новых акциях!"
            )
        )
        print(f"✅ Sent welcome message to user {user_id}")
    except Exception as e:
        print(f"❌ Could not send message to {user_id}: {e}")
    
    # 2. ПОТОМ одобряем заявку (тоже сразу, без задержек)
    try:
        await update.approve()
        print(f"✅ Approved join request for user {user_id}")
    except Exception as e:
        print(f"❌ Could not approve request for {user_id}: {e}")

# --- Обработчик команды /start для проверки ---
@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer(
        "Привет! Я бот для автоматического одобрения заявок.\n"
        "Подай заявку на вступление в канал, и я сразу одобрю её!"
    )

# --- Запуск бота ---
async def main():
    print("🚀 Starting bot...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
