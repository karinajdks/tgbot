import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import (
    InlineKeyboardMarkup, 
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove
)

BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not BOT_TOKEN:
    raise ValueError("No TELEGRAM_TOKEN found")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

CHANNEL_ID = -1004291936681
CHANNEL_LINK = "https://t.me/+sJAMqlsvbLxlOGIy"

# --- КОМАНДА /check ---
@dp.message(Command("check"))
async def check_bot_permissions(message: types.Message):
    try:
        chat_member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=bot.id)
        status = chat_member.status
        can_invite = chat_member.can_invite_users if chat_member.can_invite_users else False
        
        await message.answer(
            f"🔍 Проверка прав бота @adresanbbot:\n\n"
            f"📌 Статус: {status}\n"
            f"📌 Право 'Приглашать': {can_invite}\n"
            f"📌 ID канала: {CHANNEL_ID}"
        )
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")

# --- ОБРАБОТЧИК ЗАЯВОК ---
@dp.chat_join_request()
async def handle_join_request(update: types.ChatJoinRequest):
    user_id = update.from_user.id
    user_name = update.from_user.first_name
    
    print(f"📩 New join request from user {user_id} ({user_name})")
    
    # Проверяем права бота
    try:
        bot_member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=bot.id)
        if bot_member.status != "administrator":
            print(f"❌ Бот НЕ администратор!")
            return
        if not bot_member.can_invite_users:
            print(f"❌ Нет права 'Приглашать'!")
            return
    except Exception as e:
        print(f"❌ Ошибка прав: {e}")
        return
    
    # 1. ОТПРАВЛЯЕМ СООБЩЕНИЕ С БОЛЬШОЙ КНОПКОЙ (Reply Keyboard)
    try:
        # Создаем большую кнопку внизу экрана
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="✅ Я ЧЕЛОВЕК!")]  # Одна большая кнопка
            ],
            resize_keyboard=True,  # Подгоняем размер
            one_time_keyboard=True  # Кнопка исчезнет после нажатия
        )
        
        await bot.send_message(
            chat_id=user_id,
            text=(
                f"{user_name}, подтвердите, что вы не робот 🤖"
            ),
            reply_markup=keyboard
        )
        print(f"✅ Verification message sent to user {user_id}")
    except Exception as e:
        print(f"❌ Could not send message: {e}")
        try:
            await bot.approve_chat_join_request(chat_id=CHANNEL_ID, user_id=user_id)
        except Exception as e2:
            print(f"❌ Could not approve: {e2}")

# --- ОБРАБОТЧИК НАЖАТИЯ КНОПКИ "Я ЧЕЛОВЕК!" ---
@dp.message(lambda message: message.text == "✅ Я ЧЕЛОВЕК!")
async def process_human_button(message: types.Message):
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    
    print(f"🔘 User {user_id} ({user_name}) pressed 'Я ЧЕЛОВЕК!'")
    
    # Убираем клавиатуру
    try:
        await bot.send_message(
            chat_id=user_id,
            text="✅",
            reply_markup=ReplyKeyboardRemove()
        )
        print(f"✅ Removed keyboard")
    except Exception as e:
        print(f"❌ Could not remove keyboard: {e}")
    
    # 2. ОТПРАВЛЯЕМ СООБЩЕНИЕ С ДОСТУПОМ И КНОПКОЙ "ПЕРЕЙТИ В КАНАЛ"
    try:
        # Зеленая кнопка (Inline кнопка со ссылкой)
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(
                    text="📢 Перейти в канал", 
                    url=CHANNEL_LINK
                )]
            ]
        )
        
        await bot.send_message(
            chat_id=user_id,
            text=(
                "✅ Вам предоставлен доступ в закрытый канал!\n\n"
                "🏢 Лучшие акции и предложения от застройщиков Казани"
            ),
            reply_markup=keyboard
        )
        print(f"✅ Access message sent to user {user_id}")
    except Exception as e:
        print(f"❌ Could not send access message: {e}")
    
    # 3. ОДОБРЯЕМ ЗАЯВКУ
    try:
        await bot.approve_chat_join_request(chat_id=CHANNEL_ID, user_id=user_id)
        print(f"✅ Join request approved for user {user_id}")
    except Exception as e:
        print(f"❌ Could not approve: {e}")

# --- КОМАНДА /start ---
@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer(
        "👋 Привет! Я бот @adresanbbot.\n\n"
        "Чтобы получить доступ в закрытый канал:\n"
        "1. Перейди по ссылке-приглашению\n"
        "2. Подай заявку на вступление\n"
        "3. Нажми кнопку 'Я ЧЕЛОВЕК!'\n"
        "4. Получи доступ!\n\n"
        f"📌 {CHANNEL_LINK}"
    )

# --- ЗАПУСК ---
async def main():
    print("🚀 Starting bot @adresanbbot...")
    print(f"📌 Channel ID: {CHANNEL_ID}")
    print(f"📌 Channel Link: {CHANNEL_LINK}")
    
    try:
        bot_member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=bot.id)
        print(f"🔍 Bot status: {bot_member.status}")
        if bot_member.status == "administrator" and bot_member.can_invite_users:
            print(f"✅ Все права в порядке!")
        else:
            print(f"❌ Проверьте права бота!")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
