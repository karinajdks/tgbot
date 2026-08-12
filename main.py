import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- ТОКЕН БОТА ---
BOT_TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not BOT_TOKEN:
    raise ValueError("No TELEGRAM_TOKEN found")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- НАСТРОЙКИ КАНАЛА ---
CHANNEL_ID = -1004291936681  # ID вашего канала
CHANNEL_LINK = "https://t.me/+sJAMqlsvbLxlOGIy"  # Ссылка на канал

# --- ДИАГНОСТИКА: команда для проверки прав бота ---
@dp.message(Command("check"))
async def check_bot_permissions(message: types.Message):
    try:
        chat_member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=bot.id)
        status = chat_member.status
        can_invite = chat_member.can_invite_users if chat_member.can_invite_users else False
        
        await message.answer(
            f"🔍 Проверка прав бота @adresanbbot в канале:\n\n"
            f"📌 Статус: {status}\n"
            f"📌 Право 'Приглашать участников': {can_invite}\n"
            f"📌 ID канала: {CHANNEL_ID}\n"
            f"📌 Ссылка: {CHANNEL_LINK}\n\n"
            f"✅ Если статус 'administrator' и право 'Приглашать участников' = True - всё правильно!\n"
            f"❌ Если нет - добавьте бота в администраторы канала с этим правом!"
        )
    except Exception as e:
        await message.answer(f"❌ Ошибка при проверке: {e}")

# --- ОБРАБОТЧИК ЗАЯВОК НА ВСТУПЛЕНИЕ ---
@dp.chat_join_request()
async def handle_join_request(update: types.ChatJoinRequest):
    user_id = update.from_user.id
    user_name = update.from_user.first_name
    
    print(f"📩 New join request from user {user_id} ({user_name})")
    print(f"📌 Channel ID: {CHANNEL_ID}")
    
    # Проверяем права бота
    try:
        bot_member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=bot.id)
        print(f"🔍 Bot status in channel: {bot_member.status}")
        if bot_member.status != "administrator":
            print(f"❌ Бот НЕ администратор канала! Статус: {bot_member.status}")
            return
        if not bot_member.can_invite_users:
            print(f"❌ У бота нет права 'Приглашать участников'!")
            return
        print(f"✅ Права бота в порядке")
    except Exception as e:
        print(f"❌ Ошибка при проверке прав бота: {e}")
        return
    
    # 1. ОТПРАВЛЯЕМ СООБЩЕНИЕ С КНОПКОЙ
    try:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="✅ Я НЕ РОБОТ", callback_data="verify_human")]
            ]
        )
        
        print(f"📤 Sending verification message to user {user_id}...")
        await bot.send_message(
            chat_id=user_id,
            text=(
                f"{user_name}, подтвердите, что вы не робот 🤖\n\n"
                "Нажмите на кнопку ниже:"
            ),
            reply_markup=keyboard
        )
        print(f"✅ Verification message sent to user {user_id}")
    except Exception as e:
        print(f"❌ Could not send message to {user_id}: {e}")
        # Если не удалось отправить, всё равно одобряем заявку
        try:
            await bot.approve_chat_join_request(chat_id=CHANNEL_ID, user_id=user_id)
            print(f"✅ Join request auto-approved (without message)")
        except Exception as e2:
            print(f"❌ Could not approve: {e2}")

# --- ОБРАБОТЧИК КНОПКИ "Я НЕ РОБОТ" ---
@dp.callback_query(lambda c: c.data == "verify_human")
async def process_verify_button(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    
    print(f"🔘 User {user_id} clicked 'I AM NOT ROBOT'")
    
    # Убираем кнопку
    try:
        await bot.edit_message_reply_markup(
            chat_id=user_id,
            message_id=callback_query.message.message_id,
            reply_markup=None
        )
        print(f"✅ Removed verification button")
    except Exception as e:
        print(f"❌ Could not remove button: {e}")
    
    # 2. ОТПРАВЛЯЕМ СООБЩЕНИЕ С ДОСТУПОМ
    try:
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
        "👋 Привет! Я бот @adresanbbot для доступа в закрытый канал.\n\n"
        "Чтобы получить доступ:\n"
        "1. Перейди по ссылке-приглашению в канал\n"
        "2. Подай заявку на вступление\n"
        "3. Подтверди, что ты не робот\n"
        "4. Получи доступ!\n\n"
        f"📌 Ссылка: {CHANNEL_LINK}\n\n"
        "🔍 Напишите /check - проверить права бота"
    )

# --- ЗАПУСК ---
async def main():
    print("🚀 Starting bot @adresanbbot...")
    print(f"📌 Channel ID: {CHANNEL_ID}")
    print(f"📌 Channel Link: {CHANNEL_LINK}")
    
    # Проверка прав бота при старте
    try:
        bot_member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=bot.id)
        print(f"🔍 Bot status in channel: {bot_member.status}")
        print(f"🔍 Can invite users: {bot_member.can_invite_users}")
        if bot_member.status != "administrator":
            print(f"❌⚠️ ВНИМАНИЕ: Бот НЕ администратор канала!")
        if not bot_member.can_invite_users:
            print(f"❌⚠️ ВНИМАНИЕ: У бота нет права 'Приглашать участников'!")
        if bot_member.status == "administrator" and bot_member.can_invite_users:
            print(f"✅ Все права в порядке! Бот готов к работе.")
    except Exception as e:
        print(f"❌ Не удалось проверить права бота: {e}")
        print(f"⚠️ Убедитесь, что бот @adresanbbot добавлен в администраторы канала!")
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
