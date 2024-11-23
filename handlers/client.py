import os
from random import choice, uniform, randint
import asyncio
import datetime

from aiogram import F, Router, types, Bot
from aiogram.filters.command import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import CHANNEL_ID, REF_URL, PROMO_CODE, BOT_NAME
from keyboards.client import ClientKeyboard
from other.filters import ChatJoinFilter, RegisteredFilter
from database.db import DataBase

router = Router()


class RegisterState(StatesGroup):
    input_id = State()


class GetSignalStates(StatesGroup):
    chosing_mines = State()


@router.message(CommandStart())
async def start_command(message: types.Message, bot: Bot):
    await DataBase.register(message.from_user.id, verifed="0")
    await message.answer(f"""
Добро пожаловать, <b>{message.from_user.first_name}!</b>

Для использования бота - <b>подпишись</b> на наш канал🤝""",
                         reply_markup=await ClientKeyboard.start_keyboard(), parse_mode="HTML")


@router.callback_query(F.data.in_(["check", "back"]), ChatJoinFilter())
async def menu_output(callback: types.CallbackQuery):
    try:
        await callback.message.delete()
    except:
        pass

    await callback.message.answer(f"""

Добро пожаловать в 🔸<b>{BOT_NAME}</b>🔸!

🚀Lucky Jet🚀 – новейшее азартное развлечение которое подойдет новому поколению игроков.
Ты можешь выиграть в несколько раз больше буквально за несколько секунд!

Наш бот основан на нейросети от ChatGPT 5.0
Он может предугадать исход ракетки с вероятностью 93%.

❗️ ВНИМАНИЕ ❗️
Бот работает корректно, только с новыми аккаунтами (инструкция по регистрации есть ниже по кнопке)
❗️ ДЛЯ игры без риска ❗️
Нужен новый, чистый аккаунт, в котором при первом
депозите нужно ввести промокод <code>{PROMO_CODE}</code> который даст +500% к депозиту (инструкция по кнопке ниже)""",
                                  parse_mode="HTML", reply_markup=await ClientKeyboard.menu_keyboard())

    await callback.answer()


@router.callback_query(F.data == "register")
async def register_handler(callback: types.CallbackQuery, state: FSMContext):
    text = f"""
🔷 1. Для начала зарегистрируйтесь по ссылке на сайте <a href="{REF_URL}">1WIN</a>
🔷 2. После успешной регистрации cкопируйте ваш айди на сайте (Вкладка 'пополнение' и в правом верхнем углу будет ваш ID).
🔷 3. И отправьте его боту в ответ на это сообщение!"""
    photo = types.FSInputFile("reg.jpg")


    try:
        await callback.message.delete()
    except:
        pass

    await callback.message.answer(text, parse_mode="HTML", reply_markup=await ClientKeyboard.register_keyboard())
    await state.set_state(RegisterState.input_id)



@router.message(RegisterState.input_id)
async def register_handler_finaly(message: types.Message, state: FSMContext):

    try:
        number = int(message.text)

        if len(message.text) >= 8:
            await DataBase.update_verifed(message.from_user.id)
            await message.answer("Вы успешно зарегистрировались.", reply_markup=await ClientKeyboard.on_register_keyboard())
            await state.clear()
        else:
            print(message.text)
            await message.answer("Неверный ID")
            return

    except Exception as e:
        print(e)
        print(message.text)
        await message.answer("Неверный ID")
        return


@router.callback_query(F.data == "instruction")
async def instucrion_handler(callback: types.CallbackQuery):
    text = f"""
Бот основан и обучен на кластере нейросети 🖥 <strong>[ChatGPT 5.0]</strong>.
Для тренировки бота было сыграно 🎰10.000+ игр.

В данный момент пользователи бота успешно делают в день 15-25% от своего 💸 капитала!
<code>На текущий момент бот по сей день проходит проверки и  исправления! Точность бота составляет 92%!</code>
Для получения максимального профита следуйте следующей инструкции:

🟢 1. Пройти регистрацию в букмекерской конторе <a href="{REF_URL}">1WIN</a>
Если не открывается - заходим с включенным VPN (Швеция). В Play Market/App Store полно бесплатных сервисов, например: Vpnify, Planet VPN, Hotspot VPN и так далее!
<code>Без регистрации доступ к сигналам не будет открыт!</code>
🟢 2. Пополнить баланс своего аккаунта.
🟢 3. Перейти в раздел 1win games и выбрать игру 🚀'LUCKYJET'.
🟢 4. Посмотреть сигнал в боте и забрать согласно сигнала из бота.
🟢 5. При неудачном сигнале советуем удвоить(Х²) ставку что бы полностью перекрыть потерю при следующем сигнале."""

    photo = types.FSInputFile("instruction.jpg")

    try:
        await callback.message.delete()
    except:
        pass

    await callback.message.answer_photo(photo, text, reply_markup=await ClientKeyboard.back_keyboard(), parse_mode="HTML")


@router.callback_query(F.data == "get_signal")
async def get_signal_start_handler(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id

    user_data = await DataBase.get_user(user_id)
    
    if user_data:
        await callback.message.answer("Добро пожаловать! Вы можете начать пользоваться сигналами.",
                                      reply_markup=await ClientKeyboard.get_signal_keyboard())
    else:
        await register_handler(callback, state)
