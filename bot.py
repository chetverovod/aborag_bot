import asyncio
import logging
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram import F
from aiogram.types import Message
from aiogram import html
from aiogram.types.input_file import FSInputFile
from aiogram.types import InputFile
import config
import keyboard as kb
import model_io as mio


# Load settings from configuration file.
cfg = config.Config('bot_settings.cfg')
TETOKEN = cfg['tetoken']
BOT_TAG = f"bot<{cfg['bot_name']}>"

VER = "0.1.1"

HELP_MSG = "Просто напишите вопрос и бот ответит, основываясь только" \
           " на сведениях, указанных в руководстве по эксплуатации."

MOTO_BIKES = ['Suzuki Djebel 200']

link_to_service_manual = 'https://disk.yandex.ru/i/gWonEIVopPJnGA'

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

# Объект бота
bot = Bot(token=TETOKEN)

# Диспетчер
dp = Dispatcher()


def init():
    """Initial settings for start."""
# Делаем запись в лог о старте бота. Туда же будут
# помещены запросы и ответы:
    with open(cfg['log_file'], 'a', encoding='utf-8') as f:
        time_begin = datetime.now()
        f.write(f"\n{time_begin} {BOT_TAG} - start\n")


@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    """ Process /help command."""

    await message.reply(HELP_MSG)


@dp.message(Command("ver"))
async def cmd_verp(message: types.Message):
    """Process `/ver` command."""

    await message.reply(VER)


@dp.message(Command('keyboard'))
async def process_keyboard_command(message: types.Message):
    """Process /keyboard command."""
    await message.reply("Привет!", reply_markup=kb.greet_kb)


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Process `/start` command."""

    await message.answer("Привет!\n Этот бот отвечает на вопросы"
                         + " по обслуживанию мотоциклов"
                         + " пока только одной модели:"
                         + f" {MOTO_BIKES}.\nПока только по первым двум "
                         + "главам руководства"
                         + f" по эксплуатации:{link_to_service_manual}\n"
                         + f"{HELP_MSG}"
                         )


@dp.message(F.text)
async def handle_user_query(message: Message, bot: Bot):
    """Handle user queries."""

    # Получаем текущее время в часовом поясе ПК
    time_begin = datetime.now()
    query = message.text
    print(f'Query: {query}')
    with open(cfg['log_file'], 'a', encoding='utf-8') as f:
        f.write(f"\n{time_begin} bot<{cfg['bot_name']}> - "
                + f"user<{message.from_user.username}> - "
                + f"query<{query}>\n")

    model_answer = mio.make_answer(query)
    time_end = datetime.now()
    time_dif = time_begin - time_end
    seconds_in_day = 24 * 60 * 60
    work_time = divmod(time_dif.days * seconds_in_day + time_dif.seconds, 60)
    print(f'Working time: {abs(work_time[0])} minutes {abs(work_time[1])}'
          + ' seconds.')
    with open(cfg['log_file'], 'a', encoding='utf-8') as f:
        f.write(f"\n{time_end} bot<{cfg['bot_name']}> - "
                + f"user<{message.from_user.username}> - "
                + f"answer<{model_answer}>\n")
    await message.answer(model_answer)


async def main():
    """Start bot."""
    init()
    # Запуск процесса поллинга новых апдейтов
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
