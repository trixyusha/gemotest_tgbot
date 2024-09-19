import re
from time import monotonic

from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.methods.delete_message import DeleteMessage
# from aiogram.types.input_file import BufferedInputFile as send_buffer

from app.handlers_user.main_handlers import router
from app.database.requests.main_requests import get_hash_data, set_user
from ..keyboards_user.default_keyboard import default_keyboard_builder

from app.send_sms import SMSC
from app.send_sms import get_kod as code



class Confirm_Number(StatesGroup):
    p_number = State()
    confirm_code = State()
    time = State()
    resend = State()

# пользователю приходит сообщение и документ с согласием на обработку персональных данных, обработка кнопок "соглашаюсь" и "не соглашаюсь"
@router.callback_query(F.data.regexp(r'\b[sid]{,3}agree\b'))
async def activate_the_service_disagree(callback: CallbackQuery, state: FSMContext) -> None:
    if 'dis' in callback.data:
        await callback.answer()
        await callback.message.answer('Согласие на обработку персональных данных отклонено. Подключение услуги невозможно.')
        try:
            return DeleteMessage(chat_id = callback.message.chat.id, message_id = callback.message.message_id)
        except: pass
    else:
        await state.set_state(Confirm_Number.p_number)
        await callback.answer()
        await callback.message.edit_caption(callback.inline_message_id,'Вы дали свое согласие на обработку персональных данных!',
                                            reply_markup = None)
        await callback.message.answer('Отправьте свой номер телефона, чтобы подключить услугу <b>"Отправка результатов исследований в Telegram"</b>.', 
                                        parse_mode = 'HTML', 
                                        reply_markup =  await default_keyboard_builder(
                                            text = '📱Отправить номер телефона',
                                            sizes = 1,
                                            request_cont = True,
                                            resize_keyboard = True,
                                            input_field_placeholder = 'Отправьте номер телефона...'
                                        )
                                    )

# пользователь отправил свой номер телефона    
@router.message(Confirm_Number.p_number, F.contact)
@router.message(Confirm_Number.p_number, F.text.regexp(r'\d+'))
async def get_contact(message: Message, state: FSMContext) -> None:
    smsc = SMSC()
    ccode = code()
    sms_text = f'Никому не говорите код {ccode}! Авторизация в боте https://t.me/GemotestLaboratory_Bot.'
    # cost = smsc.get_sms_cost(message.contact.phone_number[1:], sms_text)
    # print(re.findall(r'^(\+7|7|8)?[\s\-]?\(?[489][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$', message.contact.phone_number))
    if message.contact:
        if '+' in message.contact.phone_number:
            await state.update_data(p_number = message.contact.phone_number[1:])
            # smsc.send_sms(message.contact.phone_number[1:], sms_text)
            start_time = monotonic()
            print(f'\n\nPHONE NUMBER {message.contact.phone_number[1:]}\n-----------\nTEXT\n{sms_text}\n-----------\n\n')
            await state.set_state(Confirm_Number.confirm_code)
            await state.update_data(confirm_code = ccode, time = start_time)
        else:
            await state.update_data(p_number = message.contact.phone_number)
            # smsc.send_sms(message.contact.phone_number, sms_text)
            start_time = monotonic()
            print(f'\n\nTIME {start_time}\n-----------\nPHONE NUMBER {message.contact.phone_number}\n-----------\nTEXT\n{sms_text}\n-----------\n\n')
            await state.set_state(Confirm_Number.confirm_code)
            await state.update_data(confirm_code = ccode, time = start_time)
        # Код действителен в течение 15 минут, после чего подключение услуги будет автоматически отменено.
    elif message.text:
        if bool(re.match(r'^(\+7|8)\s?\(?9[0-9]{2}\)?\s?((\s|-)?[0-9]){7}', message.text)):
            await state.update_data(p_number = message.text)
            # smsc.send_sms(message.contact.phone_number, sms_text)
            start_time = monotonic()
            print(f'\n\nTIME {start_time}\n-----------\nPHONE NUMBER {message.text}\n-----------\nTEXT\n{sms_text}\n-----------\n\n')
            await state.set_state(Confirm_Number.confirm_code)
            await state.update_data(confirm_code = ccode, time = start_time)
        else: 
            await message.answer('Неверный номер телефона, введите снова или нажмите на кнопку <b>"Отправить номер телефона"</b>', parse_mode = 'HTML')
            await state.get_state(Confirm_Number.p_number)
    await message.answer('''Для подтверждения номера телефона, вам придет код в SMS-сообщении, который необходимо будет отправить в этот чат.
Код действителен в течение 15 минут.''', reply_markup = ReplyKeyboardRemove())
    try:
        return DeleteMessage(chat_id = message.chat.id, message_id = message.message_id)
    except: pass


# пользователь отправляет код подтверждения, который ему был выслан в смс сообщении    
@router.message(Confirm_Number.confirm_code)
async def confirmation(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    if monotonic() - data['time'] < float(15*60): # 15*60
        print(f'\n\nNEW IF TIME {monotonic()-data["time"]}\n\n')
        if data['confirm_code']  ==  message.text:
            await message.answer('Услуга <b>"Отправка результатов исследований в Telegram"</b> подключена!', parse_mode = 'HTML', 
                                    reply_markup = await default_keyboard_builder(
                                        text = ['📝Оформить предварительный заказ','🛒Корзина','🧾Заказы','⚙️Помощь','❌Отключиться от услуги'],
                                        sizes = [1,2,1,1],
                                        input_field_placeholder = 'Выберите пункт меню...',
                                        resize_keyboard = True
                                    )
                                )
            await set_user(message.from_user.id, phone_number = get_hash_data(data['p_number']))
            await state.clear()
        else:
            await message.answer('Неверный код, повторите попытку ввода.', reply_markup = None)
    else:
        await message.answer('''15 минут прошло, код больше не является действительным.
Отправить повторно?''', reply_markup = await default_keyboard_builder(text = ['Да', 'Нет'], callback_data = ['yes_resend', 'no_resend']))
        await state.set_state(Confirm_Number.resend)

# код не действителен
@router.callback_query(Confirm_Number.resend, F.data.regexp(r'\w{2,3}_resend'))
async def re_sending_code(callback: CallbackQuery, state: FSMContext):
    if 'no' in callback.data:
        await callback.answer()
        await callback.message.answer('Услуга <b>"Отправка результатов исследований в Telegram"</b> не была подключена.', parse_mode = 'HTML', reply_markup = await default_keyboard_builder(
                                text = ['📝Оформить предварительный заказ','🛒Корзина','🧾Заказы','⚙️Помощь','🆕Подключить получение результатов'],
                                sizes = [1,2,1,1],
                                input_field_placeholder = 'Выберите пункт меню...',
                                resize_keyboard = True
                            ))
        await state.clear()
        try:
            return DeleteMessage(chat_id = callback.message.chat.id, message_id = callback.message.message_id)
        except: pass
    elif 'yes' in callback.data:
        smsc = SMSC()
        ccode = code()
        sms_text = f'Никому не говорите код {ccode}! Авторизация в боте https://t.me/GemotestLaboratory_Bot.'
        data = await state.get_data()
        await callback.answer()
        start_time = monotonic()
        print(f'\n\nPHONE NUMBER {data["p_number"]}\n-----------\nTEXT\n{sms_text}\n-----------\n\n')
        await state.set_state(Confirm_Number.confirm_code)
        await state.update_data(confirm_code = ccode, time = start_time)
        await callback.message.edit_text('Код отправлен повторно. Он также действителен 15 минут.', reply_markup = None)