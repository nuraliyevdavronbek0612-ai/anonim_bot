import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove
)

TOKEN = "8518179111:AAHuU-KG1N7VoeT7af9eRiG939Ikm3vgHJY"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ====== MA'LUMOTLAR ======
users = {}
waiting = []
chats = {}

# ====== STATES ======
class Register(StatesGroup):
    gender = State()
    age = State()
    goal = State()

# ====== KEYBOARDS ======
gender_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="👨 Erkak", callback_data="gender_erkak"),
            InlineKeyboardButton(text="👩 Ayol", callback_data="gender_ayol"),
        ]
    ]
)

goal_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="💍 Oila qurish", callback_data="goal_oila")],
        [InlineKeyboardButton(text="❤️ Sevgi", callback_data="goal_sevgi")],
        [InlineKeyboardButton(text="🤝 Do‘st", callback_data="goal_dost")],
        [InlineKeyboardButton(text="🔥 Intim", callback_data="goal_intim")],
    ]
)

start_chat_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="💬 Start chat", callback_data="start_chat")]
    ]
)

stop_chat_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="❌ Suhbatni tugatish")]],
    resize_keyboard=True
)

# 🔹 QO‘SHILDI (boshlash tugmasi)
begin_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Boshlash", callback_data="begin_register")]
    ]
)

# ====== /start ======
@dp.message(Command("start"))
async def start_cmd(message: types.Message, state: FSMContext):
    await state.clear()

    await message.answer(
        "👋 Assalomu alaykum!\n\n"
        "🕶️ *Bu anonim tanishuv chat bot*.\n\n"
        "Bu yerda:\n"
        "• 🙈 Ismingiz ko‘rinmaydi\n"
        "• 🔒 Profilingiz uzatilmaydi\n"
        "• 🧑‍🤝‍🧑 Suhbatdosh sizni tanimaydi\n\n"
        "💬 Xavfsiz va to‘liq anonim tarzda bemalol suhbatlashishingiz mumkin.\n\n"
        "Boshlash uchun tugmani bosing 👇",
        parse_mode="Markdown",
        reply_markup=begin_kb
    )

# 🔹 QO‘SHILDI (boshlash bosilganda davom etadi)
@dp.callback_query(lambda c: c.data == "begin_register")
async def begin_register(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_text("Jinsingizni tanlang:")
    await callback.message.edit_reply_markup(reply_markup=gender_kb)
    await state.set_state(Register.gender)

# ====== GENDER ======
@dp.callback_query(lambda c: c.data.startswith("gender_"))
async def get_gender(callback: types.CallbackQuery, state: FSMContext):
    gender = callback.data.split("_")[1]
    await state.update_data(gender=gender)

    await callback.message.edit_text("Yoshingizni raqam bilan yozing:")
    await callback.answer()

    await state.set_state(Register.age)

# ====== AGE ======
@dp.message(Register.age)
async def get_age(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❗ Iltimos, yoshni raqam bilan yozing")
        return

    await state.update_data(age=int(message.text))

    await message.answer(
        "Maqsadingizni tanlang:",
        reply_markup=goal_kb
    )

    await state.set_state(Register.goal)

# ====== GOAL ======
@dp.callback_query(lambda c: c.data.startswith("goal_"))
async def get_goal(callback: types.CallbackQuery, state: FSMContext):
    goal = callback.data.split("_")[1]
    data = await state.get_data()

    users[callback.from_user.id] = {
        "gender": data["gender"],
        "age": data["age"],
        "goal": goal
    }

    await state.clear()
    await callback.answer()

    await callback.message.edit_text("Chatni boshlash uchun:")
    await callback.message.answer(
        "👇",
        reply_markup=start_chat_kb
    )

# ====== START CHAT ======
@dp.callback_query(lambda c: c.data == "start_chat")
async def start_chat(callback: types.CallbackQuery):
    uid = callback.from_user.id
    await callback.answer()

    if uid in chats:
        await callback.message.answer("❗ Siz allaqachon chatdasiz")
        return

    if waiting and waiting[0] != uid:
        partner = waiting.pop(0)
        chats[uid] = partner
        chats[partner] = uid

        await callback.message.answer(
            "🔗 Suhbatdosh topildi! Yozishingiz mumkin.",
            reply_markup=stop_chat_kb
        )
        await bot.send_message(
            partner,
            "🔗 Suhbatdosh topildi! Yozishingiz mumkin.",
            reply_markup=stop_chat_kb
        )
    else:
        waiting.append(uid)
        await callback.message.answer("⏳ Suhbatdosh qidirilmoqda...")

# ====== STOP CHAT ======
@dp.message(lambda m: m.text == "❌ Suhbatni tugatish")
async def stop_chat(message: types.Message):
    uid = message.from_user.id

    if uid in chats:
        partner = chats.pop(uid)
        chats.pop(partner, None)

        await message.answer(
            "❌ Suhbat tugadi.",
            reply_markup=ReplyKeyboardRemove()
        )

        await bot.send_message(
            partner,
            "❌ Suhbat tugadi.",
            reply_markup=ReplyKeyboardRemove()
        )

        await message.answer(
            "Yangi suhbat uchun:",
            reply_markup=start_chat_kb
        )
        await bot.send_message(
            partner,
            "Yangi suhbat uchun:",
            reply_markup=start_chat_kb
        )

# ====== CHAT ======
@dp.message()
async def relay(message: types.Message):
    uid = message.from_user.id
    if uid in chats:
        await bot.send_message(chats[uid], message.text)

# ====== RUN ======
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
