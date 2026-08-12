import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not BOT_TOKEN:
    raise ValueError("No TELEGRAM_TOKEN found")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# ⚠️ ЗАМЕНИТЕ ЭТО НА ID ВАШЕГО КАНАЛА
# Узнать ID можно через @userinfobot
CHANNEL_ID = -1004291936681  # <--- ПОДСТАВЬТЕ СВОЙ ID

# Ссылка на канал (для кнопки)
CHANNEL_LINK = "https://t.me/+sJAMqlsvbLxlOGIy"

# --- ОБРАБОТЧИК ЗАЯВОК ---
@dp.chat_join_request()
async def handle_join_request(update: types.ChatJoinRequest):
    user_id = update.from_user.id
    user_name = update.from_user.first_name
    
    try:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="✅ Я НЕ РОБОТ", callback_data="verify_human")]
            ]
        )
        
        await bot.send_message(
            chat_id=user_id,
            text=(
                f"{user_name}, подтвердите, что вы не робот 🤖\n\n"
                "Нажмите на кнопку ниже:"
            ),
            reply_markup=keyboard
        )
        print(f"✅ Sent verification to user {user_id}")
    except Exception as e:
        print(f"❌ Could not send message to {user_id}: {e}")
        await bot.approve_chat_join_request(chat_id=CHANNEL_ID, user_id=user_id)

# --- ОБРАБОТЧИК КНОПКИ "Я НЕ РОБОТ" ---
@dp.callback_query(lambda c: c.data == "verify_human")
async def process_verify_button(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    
    # Убираем кнопку
    await bot.edit_message_reply_markup(
        chat_id=user_id,
        message_id=callback_query.message.message_id,
        reply_markup=None
    )
    
    # Отправляем сообщение с доступом
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📢 Перейти в канал", url=CHANNEL_LINK)]
        ]
    )
    
    await bot.send_message(
        chat_id=user_id,
        text=(
            "✅ Вам предоставлен доступ в закрытый канал!\n\n"
            "🏢 Лучшие акции и предложения от застройщиков Казани\n\n"
            "Нажмите на кнопку ниже, чтобы перейти:"
        ),
        reply_markup=keyboard
    )
    
    # Одобряем заявку
    try:
        await bot.approve_chat_join_request(chat_id=CHANNEL_ID, user_id=user_id)
        print(f"✅ Approved join request for user {user_id}")
    except Exception as e:
        print(f"❌ Could not approve: {e}")

# --- Обработчик /start ---
@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer(
        "👋 Привет! Я бот для доступа в закрытый канал.\n\n"
        "Подай заявку на вступление, и я помогу тебе пройти верификацию."
    )

# --- Запуск ---
async def main():
    print("🚀 Starting bot...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
