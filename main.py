import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# Токен берется из переменной окружения (безопасно)
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

    try:
        # 1. Отправляем приветственное сообщение в личку пользователю
        await bot.send_message(
            chat_id=user_id,
            text=(
                f"Привет, {user_name}! 👋\n"
                "Добро пожаловать в закрытый канал с акциями!\n"
                "Твой запрос на вступление автоматически одобрен. 🎉"
            )
        )
        print(f"Sent welcome message to user {user_id}")

        # 2. Одобряем заявку на вступление в канал
        await update.approve()
        print(f"Approved join request for user {user_id}")

    except Exception as e:
        print(f"Error for user {user_id}: {e}")
        # Если не удалось отправить сообщение, всё равно одобряем заявку
        await update.approve()

# --- Обработчик команды /start для проверки ---
@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer("Привет! Я бот для автоматического одобрения заявок в канал.")

# --- Запуск бота ---
async def main():
    print("Starting bot...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
