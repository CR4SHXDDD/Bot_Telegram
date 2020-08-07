from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.types import Message
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import asyncio

import logging




from csv_create import *
from db_create import *
from db import *
from states.states import Find
from config import TOKEN


bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

logging.basicConfig(level=logging.INFO)

@dp.message_handler(commands=["cancel"], state=Find) # Выход из состояний
async def cancel(message: types.Message, state: FSMContext):
    await message.answer(('Вы успешно вышли' 
                          '\nДля продолжения работы с ботом введите одну из команд:' 
                          '\n/mygames - выводит игры, на рассылку которых вы подписались' 
                          '\n/find - поиск игр по названию'))


    await state.reset_state()






@dp.message_handler(state = Find.Info) #Вывод общую информацию о игре
async def find_message(msg: types.Message, state:FSMContext):


    name = msg.text
    if (search_game_equals(name) != ''):
        await bot.send_message(msg.from_user.id, 'Игра найдена: ' + search_game_equals(name))
        await state.update_data(gameName=name)

        await types.ChatActions.typing()
        await asyncio.sleep(0.6)

        await bot.send_message(msg.from_user.id, information_conclusion(name))
        await bot.send_photo(msg.from_user.id, types.InputFile.from_url(get_photo(name)))
        markup = types.InlineKeyboardMarkup(
            inline_keyboard=[
                [types.InlineKeyboardButton(text=("Да"), callback_data="Yes")],
                [types.InlineKeyboardButton(text=("Нет"), callback_data="No")]
            ]
        )
        await bot.send_message(msg.from_user.id,"Хотите получать рассылку новостей по этой игре?" , reply_markup=markup)
        await Find.Distribution.set()

    elif(search_game(name)):
        markup = types.InlineKeyboardMarkup(
            inline_keyboard=[
                [types.InlineKeyboardButton(text=("Да"), callback_data = "Yes")], [types.InlineKeyboardButton(text=("Нет"), callback_data = "No")]
           ]
        )
        name = search_game(name)
        await bot.send_message(msg.from_user.id, 'Вы имели ввиду эту игру: ' + name + '?', reply_markup= markup)
        await state.update_data(gameName=name)

    else:
        await bot.send_message(msg.from_user.id, "К сожалению, я не нашел такой игры")
        await bot.send_message(msg.from_user.id, "Введите название игры или нажмите /cancel")
        await Find.Info.set()




@dp.callback_query_handler(text_contains="Yes", state=Find.Info) #Вывод инофрмации об игре; согласие на рассылку
async def yes_game(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()

    a = await state.get_data()

    await types.ChatActions.typing()
    await asyncio.sleep(0.6)
    await call.message.answer(information_conclusion(a['gameName']))
    await bot.send_photo(call.from_user.id,  types.InputFile.from_url(get_photo(a['gameName'])))



    markup = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text=("Да"), callback_data="Yes")],
            [types.InlineKeyboardButton(text=("Нет"), callback_data="No")]
        ]
    )
    await call.message.answer("Хотите получать рассылку новостей по этой игре", reply_markup=markup)



    await Find.Distribution.set()





@dp.callback_query_handler(text_contains="No", state=Find.Info) #отказ пользователя от предложенной игры; перенаправение на ввод игры
async def no_game(call: types.CallbackQuery):
    await call.message.answer("Введите название игры или нажмите /cancel")
    await call.message.edit_reply_markup()

    await Find.Info.set()



@dp.callback_query_handler(text_contains="Yes", state=Find.Distribution) #Вывод последней статьи и подписка на рассылку статей
async def yes(call: types.CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup()



    async def add_games():
        if (add_game(call.from_user.id, a['gameName'], data['url'])):
            await call.message.answer("Игра добавлена в список рассылаемых")
            await call.message.answer("Введите название игры или нажмите /cancel")
        else:
            await call.message.answer("Эта игра уже была добавлена в ваш список ранее")
            await call.message.answer("Введите название игры или нажмите /cancel")




    a = await state.get_data()
    select = Game.get(Game.name == a['gameName'])
    data =  parser_post(select.url)
    if (data['counter'] > 1):
        await types.ChatActions.typing()
        await asyncio.sleep(0.6)
        media = types.MediaGroup()
        for i in data['image']:
            media.attach_photo(types.InputFile.from_url(i))

        await types.ChatActions.typing()
        await asyncio.sleep(0.6)
        await call.message.answer((data['title'] + '.\n' + data['info'] + '.\n' + data['video']))
        await bot.send_media_group(call.from_user.id, media)
        await add_games()

    else:

        await types.ChatActions.typing()
        await asyncio.sleep(0.6)

        await call.message.answer((data['title'] + '.\n' + data['info'] + '.\n' + data['video']))
        if (data['image']):
            await bot.send_photo(call.from_user.id, types.InputFile.from_url(data['image'][0]))
        await add_games()


    await Find.Info.set()







@dp.callback_query_handler(text_contains="No", state=Find.Distribution)#Пользователь отказался от рассылки; перенаправен на ввод игры
async def no(call: types.CallbackQuery):
    await call.message.answer("Введите название игры или нажмите /cancel")
    await call.message.edit_reply_markup()
    await Find.Info.set()




@dp.message_handler(commands=['find']) # Начало поиска игр
async def find_message(msg: types.Message):

    await bot.send_message(msg.from_user.id, "Введите название игры или нажмите /cancel")

    await Find.Info.set()


@dp.message_handler(commands=['start']) # Команда старт
async def process_start_command(message: types.Message):
    await message.reply("Привет!\nЯ создан для того, чтобы рассказать тебе об играх, которые скоро выйдут"
                        '\nДля продолжения работы с ботом введите одну из команд:'
                        '\n/find - поиск игр по названию'
                        '\n/help - вывод всех доступных комманд')


@dp.message_handler(commands=['help']) # Команда помощи
async def process_help_command(message: types.Message):
    await message.reply('Бот поддерживает следующие команды:'
                     '\n /mygames - выводит игры, на рассылку которых вы подписались'
                     '\n /find - поиск игр по названию')


@dp.message_handler(commands=['mygames']) # Команда, выводящая игры, на которые подписан пользователь
async def find_message(msg: types.Message):
    await bot.send_message(msg.from_user.id, print_game(msg.from_user.id))



@dp.message_handler()
async def other_echo(message: Message):
    await message.reply('Я не понимаю вас')


async def renewal_post(wait_for): #рассылка новых статей
    while True:
        await asyncio.sleep(wait_for)

        id, data =  renovation_post()

        if (data):

            if (data['counter'] > 1):
                await asyncio.sleep(0.6)
                media = types.MediaGroup()
                for i in data['image']:
                    media.attach_photo(types.InputFile.from_url(i))

                await asyncio.sleep(0.6)
                text = data['title'] + '.\n' + data['info'] + '.\n' + data['video']
                await bot.send_message(id, text)
                await bot.send_media_group(id, media)

            else:

                await asyncio.sleep(0.6)
                text = data['title'] + '.\n' + data['info'] + '.\n' + data['video']
                await bot.send_message(id, text)
                if (data['image']):
                    await bot.send_photo(id, types.InputFile.from_url(data['image'][0]))





async def renewal_db(wait_for): # обновление базы данных Game
    while True:
        await asyncio.sleep(wait_for)

        clear_csv()

        create_db()





if __name__ == '__main__':



    dp.loop.create_task(renewal_post(3600))
    dp.loop.create_task(renewal_db(86000))
    executor.start_polling(dp, skip_updates=True)
