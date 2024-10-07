import sqlite3
import asyncio
import aiohttp
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, FSInputFile
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from config import TOKEN

bot = Bot(token=TOKEN)
dp = Dispatcher()

logging.basicConfig(level=logging.INFO)

class Form(StatesGroup):
    name = State()
    age = State()
    grade = State()

def init_db():
    conn = sqlite3.connect('school_data.db')
    cur = conn.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER NOT NULL,
        grade TEXT NOT NULL)''')
    conn.commit()
    conn.close()
init_db()

@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await message.answer("Привет, как тебя зовут?")
    await state.set_state(Form.name)

@dp.message(Form.name)
async def name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Сколько тебе лет?")
    await state.set_state(Form.age)

@dp.message(Form.age)
async def age(message: Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.answer("Какой у тебя класс?")
    await state.set_state(Form.grade)

@dp.message(Form.grade)
async def grade(message: Message, state: FSMContext):
    await state.update_data(grade=message.text)
    user_data = await state.get_data()

    conn = sqlite3.connect('school_data.db')
    cur = conn.cursor()

    cur.execute('''
        INSERT INTO users (name, age, grade) VALUES (?, ?, ?)''', (user_data['name'], user_data['age'], user_data['grade']))
    conn.commit()
    conn.close()

    await message.answer("Твои данные успешно сохранены!")

@dp.message(Command('view_data'))
async def view_data(message: Message):
    conn = sqlite3.connect('school_data.db')
    cur = conn.cursor()

    cur.execute("SELECT * FROM users")
    rows = cur.fetchall()  # Извлекаем все строки из таблицы

    conn.close()

    if rows:
        response = "Записанные данные:\n\n"
        for row in rows:
            response += f"ID: {row[0]}, Имя: {row[1]}, Возраст: {row[2]}, Класс: {row[3]}\n"
        await message.answer(response)
    else:
        await message.answer("В базе данных пока нет записей.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
