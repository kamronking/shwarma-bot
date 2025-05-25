from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.client.default import DefaultBotProperties
import asyncio
import random

bot = Bot(token="8066605282:AAGKQuzX6JKTC6tdOwhPMH8jbkufZt4lzQo", default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

# Блюда
menu = {
    "🥙 Kichik Lavash": {"description": "Mazali kichik lavash", "price": 20000},
    "🌯 Katta Lavash": {"description": "To‘yimli katta lavash", "price": 30000},
    "🍟 Fri Kartoshka": {"description": "Yangi pishirilgan fri", "price": 12000},
}

# Хранилище для заказов (в памяти)
user_data = {}

# Главное меню
@dp.message(F.text == "/start")
async def start(message: types.Message):
    user_data[message.from_user.id] = {"cart": [], "step": "menu"}
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=title, callback_data=f"add_{title}")] for title in menu.keys()
    ])
    await message.answer("🍽 <b>Shawarma King menyusi:</b>\nTanlang:", reply_markup=kb)

# Обработка добавления в корзину
@dp.callback_query(F.data.startswith("add_"))
async def add_to_cart(callback: types.CallbackQuery):
    item = callback.data.replace("add_", "")
    user_id = callback.from_user.id
    user_data[user_id]["cart"].append(item)

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Yana qo‘shish", callback_data="more")],
        [InlineKeyboardButton(text="✅ Buyurtma berish", callback_data="order")]
    ])
    await callback.message.edit_text(f"✅ <b>{item}</b> savatga qo‘shildi!\nYana qo‘shasizmi yoki buyurtma berasizmi?", reply_markup=kb)

# Продолжить или оформить заказ
@dp.callback_query(F.data == "more")
async def show_menu_again(callback: types.CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=title, callback_data=f"add_{title}")] for title in menu.keys()
    ])
    await callback.message.edit_text("🍽 Yana biror narsa tanlang:", reply_markup=kb)

@dp.callback_query(F.data == "order")
async def request_name(callback: types.CallbackQuery):
    user_data[callback.from_user.id]["step"] = "ask_name"
    await callback.message.answer("📝 Iltimos, ismingizni yozing:")

# Обработка имени
@dp.message(F.text, lambda msg: user_data.get(msg.from_user.id, {}).get("step") == "ask_name")
async def get_name(message: types.Message):
    user_data[message.from_user.id]["name"] = message.text
    user_data[message.from_user.id]["step"] = "ask_phone"
    kb = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 Raqamni yuborish", request_contact=True)]],
        resize_keyboard=True, one_time_keyboard=True
    )
    await message.answer("📞 Iltimos, telefon raqamingizni yuboring:", reply_markup=kb)

# Обработка номера
@dp.message(F.contact)
async def get_contact(message: types.Message):
    user = user_data.get(message.from_user.id, {})
    name = user.get("name", "Noma’lum")
    phone = message.contact.phone_number
    items = user.get("cart", [])
    total = sum([menu[i]["price"] for i in items])
    order_number = random.randint(1000, 9999)

    text = f"✅ <b>Buyurtma qabul qilindi!</b>\n\n"
    text += f"👤 Ism: {name}\n📞 Telefon: {phone}\n\n🛒 Savat:\n"
    for item in items:
        text += f"• {item} - {menu[item]['price']} so'm\n"
    text += f"\n💰 Umumiy: {total} so'm\n🆔 Buyurtma raqami: #{order_number}"

    await message.answer(text, reply_markup=ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="/start")]], resize_keyboard=True))
    user_data[message.from_user.id] = {"cart": [], "step": "menu"}

# Запуск бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
