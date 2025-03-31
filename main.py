import logging
from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
import os
from dotenv import load_dotenv
import random

# Загружаем переменные окружения из .env файла
# Я всегда использую этот подход, чтобы не хранить токены в коде
load_dotenv()

# Настраиваем логирование
logging.basicConfig(level=logging.INFO)

# Берём токен бота из переменных окружения
TOKEN = os.getenv("BOT_TOKEN")

# Инициализируем бота и диспетчер
bot = Bot(token=TOKEN)
# В aiogram 3.x используем новый способ создания диспетчера с хранилищем в памяти
dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)

# Состояния для конечного автомата (FSM)
# Каждое состояние соответствует одному вопросу теста
class SuperheroTest(StatesGroup):
    question1 = State()  # Первый вопрос
    question2 = State()  # Второй вопрос
    question3 = State()  # Третий вопрос
    question4 = State()  # Четвертый вопрос
    question5 = State()  # Пятый вопрос

# Вопросы и варианты ответов
# Каждый вариант ответа имеет баллы для разных супергероев
# Я долго думал над вопросами, чтобы сделать их максимально забавными :)
questions = [
    {
        "text": "Что бы ты выбрал в качестве суперспособности?",
        "options": [
            {"text": "Невидимость", "points": {"batman": 1, "superman": 0, "spiderman": 0, "ironman": 0, "deadpool": 2}},
            {"text": "Суперсила", "points": {"batman": 0, "superman": 3, "spiderman": 1, "ironman": 0, "deadpool": 0}},
            {"text": "Полёт", "points": {"batman": 0, "superman": 2, "spiderman": 0, "ironman": 2, "deadpool": 0}},
            {"text": "Гениальный ум", "points": {"batman": 3, "ironman": 3, "superman": 0, "spiderman": 1, "deadpool": 0}},
        ]
    },
    {
        "text": "Какой стиль борьбы со злом тебе ближе?",
        "options": [
            {"text": "Технологии и гаджеты", "points": {"batman": 2, "ironman": 3, "superman": 0, "spiderman": 1, "deadpool": 0}},
            {"text": "Грубая сила и неуязвимость", "points": {"batman": 0, "superman": 3, "ironman": 1, "spiderman": 0, "deadpool": 2}},
            {"text": "Юмор и харизма", "points": {"batman": 0, "superman": 0, "ironman": 1, "spiderman": 2, "deadpool": 3}},
            {"text": "Ловкость и интуиция", "points": {"batman": 1, "superman": 0, "ironman": 0, "spiderman": 3, "deadpool": 1}},
        ]
    },
    {
        "text": "Твой любимый цвет костюма для супергероя?",
        "options": [
            {"text": "Чёрный", "points": {"batman": 3, "superman": 0, "ironman": 0, "spiderman": 0, "deadpool": 0}},
            {"text": "Красный с синим", "points": {"batman": 0, "superman": 3, "spiderman": 2, "ironman": 0, "deadpool": 0}},
            {"text": "Красный с золотым", "points": {"batman": 0, "superman": 0, "ironman": 3, "spiderman": 0, "deadpool": 0}},
            {"text": "Красный", "points": {"batman": 0, "superman": 0, "ironman": 0, "spiderman": 0, "deadpool": 3}},
        ]
    },
    {
        "text": "Какое качество в людях ты ценишь больше всего?",
        "options": [
            {"text": "Справедливость", "points": {"batman": 2, "superman": 3, "ironman": 0, "spiderman": 1, "deadpool": 0}},
            {"text": "Интеллект", "points": {"batman": 2, "ironman": 3, "superman": 0, "spiderman": 1, "deadpool": 0}},
            {"text": "Преданность", "points": {"batman": 1, "superman": 2, "ironman": 0, "spiderman": 3, "deadpool": 0}},
            {"text": "Чувство юмора", "points": {"batman": 0, "superman": 0, "ironman": 2, "spiderman": 1, "deadpool": 3}},
        ]
    },
    {
        "text": "Как бы ты проводил свободное время?",
        "options": [
            {"text": "Изобретая что-то новое", "points": {"batman": 2, "ironman": 3, "superman": 0, "spiderman": 1, "deadpool": 0}},
            {"text": "Помогая нуждающимся", "points": {"batman": 1, "superman": 3, "ironman": 0, "spiderman": 2, "deadpool": 0}},
            {"text": "Тренируясь и совершенствуясь", "points": {"batman": 3, "superman": 1, "ironman": 1, "spiderman": 2, "deadpool": 0}},
            {"text": "Развлекаясь и шутя", "points": {"batman": 0, "superman": 0, "ironman": 1, "spiderman": 1, "deadpool": 3}},
        ]
    },
]

# Результаты теста
# Для каждого супергероя прописал забавное и креативное описание
superhero_results = {
    "batman": {
        "name": "Бэтмен",
        "description": "Ты - Тёмный рыцарь! Бесстрашный и расчетливый, ты полагаешься на свой интеллект и подготовку. Справедливость для тебя превыше всего, и ты готов на всё ради защиты невинных. Возможно, у тебя в шкафу есть плащ... или как минимум чёрная футболка."
    },
    "superman": {
        "name": "Супермен",
        "description": "Ты - Человек из стали! Сильный и благородный, ты всегда готов прийти на помощь и сделать мир лучше. Твоё чувство справедливости и непоколебимая моральная позиция делают тебя образцом для подражания. Только не забывай время от времени снимать очки, чтобы все не догадались о твоей истинной сущности!"
    },
    "ironman": {
        "name": "Железный человек",
        "description": "Ты - Тони Старк! Гениальный изобретатель с отличным чувством стиля. Твой острый ум и технические навыки помогают тебе решать сложные проблемы, а харизма покоряет окружающих. Возможно, у тебя дома есть мастерская и недостроенные гаджеты... или как минимум коллекция умных устройств."
    },
    "spiderman": {
        "name": "Человек-паук",
        "description": "Ты - дружелюбный сосед Человек-паук! Ты находчивый, умный и обладаешь отличным чувством юмора даже в сложных ситуациях. Тебе важны близкие люди, и ты готов на всё, чтобы защитить их. И да, ты точно фильтруешь свои селфи перед публикацией!"
    },
    "deadpool": {
        "name": "Дэдпул",
        "description": "Ты - Болтливый наёмник! Твоё чувство юмора не знает границ, как и твоя непредсказуемость. Ты идёшь своим путём, не особо заботясь о правилах и условностях. В твоём холодильнике наверняка есть чимичанги, а твои друзья знают, что с тобой никогда не бывает скучно!"
    }
}

# Функция для создания клавиатуры с вариантами ответов
def create_options_keyboard(options):
    # Создаем кнопки из вариантов ответов
    kb = []
    for option in options:
        kb.append([KeyboardButton(text=option["text"])])
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, one_time_keyboard=True)

# Обработчик команды /start
@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    # Сбрасываем предыдущее состояние, если оно было
    await state.clear()
    
    # Приветствуем пользователя
    await message.answer(
        "Привет! Я бот, который определит, какой ты супергерой! 🦸‍♂️\n"
        "Готов узнать свою супергеройскую сущность? Ответь на несколько вопросов, и я скажу, кто ты из супергероев!"
    )
    
    # Устанавливаем состояние первого вопроса
    await state.set_state(SuperheroTest.question1)
    
    # Отправляем первый вопрос с вариантами ответов
    await message.answer(
        f"Вопрос 1: {questions[0]['text']}", 
        reply_markup=create_options_keyboard(questions[0]["options"])
    )

# Обработчик команды /restart
@router.message(Command("restart"))
async def cmd_restart(message: Message, state: FSMContext):
    # Сбрасываем текущее состояние
    await state.clear()
    await message.answer("Начинаем тест заново!")
    
    # Запускаем тест с начала
    await cmd_start(message, state)

# Обработчик первого вопроса
@router.message(SuperheroTest.question1)
async def process_question_1(message: Message, state: FSMContext):
    answer = message.text
    
    # Ищем выбранный вариант ответа
    selected_option = None
    for option in questions[0]["options"]:
        if option["text"] == answer:
            selected_option = option
            break
    
    # Проверяем, что ответ корректный
    if not selected_option:
        await message.answer("Пожалуйста, выберите один из предложенных вариантов.")
        return
    
    # Сохраняем ответ
    await state.update_data(q1=selected_option["points"])
    
    # Переходим к следующему вопросу
    await state.set_state(SuperheroTest.question2)
    await message.answer(
        f"Вопрос 2: {questions[1]['text']}",
        reply_markup=create_options_keyboard(questions[1]["options"])
    )

# Обработчик второго вопроса
@router.message(SuperheroTest.question2)
async def process_question_2(message: Message, state: FSMContext):
    answer = message.text
    
    # Ищем выбранный вариант ответа
    selected_option = None
    for option in questions[1]["options"]:
        if option["text"] == answer:
            selected_option = option
            break
    
    # Проверяем, что ответ корректный
    if not selected_option:
        await message.answer("Пожалуйста, выберите один из предложенных вариантов.")
        return
    
    # Сохраняем ответ
    await state.update_data(q2=selected_option["points"])
    
    # Переходим к следующему вопросу
    await state.set_state(SuperheroTest.question3)
    await message.answer(
        f"Вопрос 3: {questions[2]['text']}",
        reply_markup=create_options_keyboard(questions[2]["options"])
    )

# Обработчик третьего вопроса
@router.message(SuperheroTest.question3)
async def process_question_3(message: Message, state: FSMContext):
    answer = message.text
    
    # Ищем выбранный вариант ответа
    selected_option = None
    for option in questions[2]["options"]:
        if option["text"] == answer:
            selected_option = option
            break
    
    # Проверяем, что ответ корректный
    if not selected_option:
        await message.answer("Пожалуйста, выберите один из предложенных вариантов.")
        return
    
    # Сохраняем ответ
    await state.update_data(q3=selected_option["points"])
    
    # Переходим к следующему вопросу
    await state.set_state(SuperheroTest.question4)
    await message.answer(
        f"Вопрос 4: {questions[3]['text']}",
        reply_markup=create_options_keyboard(questions[3]["options"])
    )

# Обработчик четвертого вопроса
@router.message(SuperheroTest.question4)
async def process_question_4(message: Message, state: FSMContext):
    answer = message.text
    
    # Ищем выбранный вариант ответа
    selected_option = None
    for option in questions[3]["options"]:
        if option["text"] == answer:
            selected_option = option
            break
    
    # Проверяем, что ответ корректный
    if not selected_option:
        await message.answer("Пожалуйста, выберите один из предложенных вариантов.")
        return
    
    # Сохраняем ответ
    await state.update_data(q4=selected_option["points"])
    
    # Переходим к следующему вопросу
    await state.set_state(SuperheroTest.question5)
    await message.answer(
        f"Вопрос 5: {questions[4]['text']}",
        reply_markup=create_options_keyboard(questions[4]["options"])
    )

# Обработчик пятого вопроса
@router.message(SuperheroTest.question5)
async def process_question_5(message: Message, state: FSMContext):
    answer = message.text
    
    # Ищем выбранный вариант ответа
    selected_option = None
    for option in questions[4]["options"]:
        if option["text"] == answer:
            selected_option = option
            break
    
    # Проверяем, что ответ корректный
    if not selected_option:
        await message.answer("Пожалуйста, выберите один из предложенных вариантов.")
        return
    
    # Сохраняем ответ
    await state.update_data(q5=selected_option["points"])
    
    # Рассчитываем результат
    data = await state.get_data()
    
    # Суммируем баллы для каждого супергероя
    # Прохожусь по всем ответам и собираю общий счет
    results = {"batman": 0, "superman": 0, "ironman": 0, "spiderman": 0, "deadpool": 0}
    
    for q_key, points in data.items():
        for hero, value in points.items():
            results[hero] += value
    
    # Ищем супергероя с максимальным количеством баллов
    max_points = 0
    chosen_hero = None
    
    for hero, points in results.items():
        if points > max_points:
            max_points = points
            chosen_hero = hero
    
    # Обрабатываем ситуацию, когда есть несколько героев с одинаковым количеством баллов
    # В таком случае выбираем случайного из них
    max_heroes = [hero for hero, points in results.items() if points == max_points]
    if len(max_heroes) > 1:
        chosen_hero = random.choice(max_heroes)
    
    # Отправляем результат
    hero_data = superhero_results[chosen_hero]
    await message.answer(
        f"🎉 Результат: Ты - {hero_data['name']}! 🎉\n\n{hero_data['description']}\n\nХочешь пройти тест ещё раз? Используй команду /restart",
        reply_markup=ReplyKeyboardRemove()
    )
    
    # Сбрасываем состояние
    await state.clear()

# Точка входа
async def main():
    # Запускаем бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())