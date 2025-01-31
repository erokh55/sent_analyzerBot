from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from transformers import pipeline
import asyncio
import os
from dotenv import load_dotenv

#токен бота
load_dotenv()
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
bot = Bot(token=TOKEN)
dp = Dispatcher()

#модель для анализа тональности
sentiment_pipeline = pipeline('sentiment-analysis', model='blanchefort/rubert-base-cased-sentiment')

#хранение последних 5 сообщений
#todo находить айди пользователя, чтобы выводил только его сообщения
last_messages = []

#команда /start
@dp.message(Command('start'))
async def start(message: Message):
    kb = [
        [types.KeyboardButton(text="Анализировать тональность")],
        [types.KeyboardButton(text="Вывести последние 5 сообщений")]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=kb)
    await message.answer('Привет! Выберите действие:', reply_markup=keyboard)

#обработка нажатия кнопки "Анализировать тональность"
@dp.message(lambda message: message.text == 'Анализировать тональность')
async def prompt_for_text(message: Message):
    await message.answer('Пожалуйста, отправьте текст для анализа.')

#анализ текста
@dp.message(lambda message: message.text not in ['Анализировать тональность', 'Вывести последние 5 сообщений'])
async def analyze(message: Message):
    text = message.text

    #сохранение сообщения в список
    last_messages.append(text + '\n')
    if len(last_messages) > 5:
        last_messages.pop(0)

    result = sentiment_pipeline(text)
    sentiment_label = result[0]['label']
    sentiment_score = result[0]['score']

    #отправляем результат пользователю
    await message.answer(f'Тональность текста: {sentiment_label} (оценка: {sentiment_score:.2f})')

#обработка нажатия кнопки "Вывести статистику последних 5 сообщений"
@dp.message(lambda message: message.text == 'Вывести последние 5 сообщений')
async def show_statistics(message: Message):
    if last_messages:
        stats_message = 'Последние 5 сообщений:\n' + '\n'.join(last_messages[-5:])
    else:
        stats_message = 'Нет сообщений для отображения.'
    
    await message.answer(stats_message)

#главная функция для запуска бота
async def main():
    #настройка диспетчера
    dp.message.register(start, Command('start'))
    dp.message.register(analyze)
    dp.message.register(show_statistics)
    dp.message.register(prompt_for_text)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())