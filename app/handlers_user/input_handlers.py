from aiogram.types import Message
from aiogram.types.input_file import InputFile as send_file

import app.functions as funcs
import app.database.requests.main_requests as request
from .view_orders_handlers import orders_pagination
from ..filters.symbol_or_letter import MessageMatch
import app.keyboards_user.default_keyboard as def_keyboard
from app.keyboards_admin.inline.inline_keyboards import help_button
from app.keyboards_user.inline import researches_keyboard, services_keyboard, order_cart_keyboard

from app.handlers_user.main_handlers import router

# обработка ввода с клавиатуры пользователя и нажатие кнопок
@router.message(MessageMatch(['подключить получение результатов', 'подключить услугу', 'получение результатов']))
async def activate_the_service(message: Message) -> None:
    user, phone = await request.set_user(message.from_user.id)
    if not phone:
        await message.answer_document(send_file('files\\personal_data_agreement.pdf'), 
                                        reply_markup = await def_keyboard.default_keyboard_builder(
                                            text = ['✅Соглашаюсь','❌Не соглашаюсь'], 
                                            callback_data = ['agree', 'disagree']
                                        ), 
                                        caption = 'Для начала рекомендуется установить двухэтапную аутентификацию (<b>облачный пароль</b>) в настройках.\n\nВы согласны на обработку персональных данных?', 
                                        protect_content = True, parse_mode = 'HTML'
                                    )
    else: await message.answer('Вы уже подключили услугу.')
# обработка ввода с клавиатуры пользователя и нажатие кнопок
@router.message(MessageMatch(['оформить предварительный заказ', 'оформить заказ', 'оформить заявку', 'оформить предварительную заявку']))
async def researches_or_services(message: Message) -> None:
    await message.answer('Исследования или медицинские услуги?\nДля поиска необходимо отправить примерное наименование исследования/услуги.', 
                            reply_markup = await def_keyboard.default_keyboard_builder(
                                    text = ['💉Исследования', '🧑‍⚕️Медицинские услуги', '🛍️Акции', '⏪Покинуть меню'], 
                                    callback_data = ['researches', 'services', 'actions', 'exit_or_exit'], sizes = 1
                            )
                        )
# обработка ввода с клавиатуры пользователя
@router.message(MessageMatch(['исследования', 'сдать анализы', 'исследование', 'сдать анализ', 'пройти исследование']))
async def researches_categories(message: Message) -> None:
    await message.answer('💉Иcследования\nВыберите категорию:', 
                            reply_markup = await researches_keyboard.research_categories(message.from_user.id)
                        )
# обработка ввода с клавиатуры пользователя
@router.message(MessageMatch(['медицинские услуги', 'услуги', 'медуслуги', 'мед услуги', 'мед. услуги', 'медицинская услуга', 'услуга', 'медуслуга', 'мед. услуга', 'мед услуга']))
async def services_categories(message: Message) -> None:
    await message.answer('Выберите категорию:', 
                            reply_markup = await services_keyboard.service_categories(message.from_user.id)
                        )
# обработка ввода с клавиатуры пользователя и нажатие кнопок
@router.message(MessageMatch(['помощь', 'help', 'помоги', 'помогите']))
async def cmd_help(message: Message) -> None:
    user, phone = await request.set_user(message.from_user.id)
    if phone  ==  True:
    # доставать данные, если пациент подключен, т.е. ему приходят результаты анализов в телеграм, то отправлять одно сообщение, такое как сейчас
        await message.answer('''*_Вы авторизованы и подключены к боту\._*\nКогда результаты анализов будут готовы, вы получите их в этом чате\.
Если анализов несколько, результаты будут доставлены по мере их готовности\.\n
Для повторного запроса результата исследований нажмите *"История заказов"*\.\n
Если вы больше не хотите получать результаты исследований в Telegram, нажмите *"Отключиться от услуги"*\.''', 
parse_mode = 'MarkdownV2', reply_markup = help_button)
    else:
        await message.answer('''*_Вы не авторизованы\._*\n
Если вы хотите получать результаты исследований в Telegram, нажмите *"Подключить получение результатов"*\.''', 
parse_mode = 'MarkdownV2', reply_markup = help_button)
# обработка ввода с клавиатуры пользователя и нажатие кнопок
@router.message(MessageMatch(['отключиться от услуги', 'отключить услугу', 'отключиться', 'отключить']))
async def exit_button(message: Message) -> None:
    disconnect = await request.disconnect_user(message.from_user.id)
    if disconnect:
        await message.answer('Вы отключились от услуги.', 
                                reply_markup = await def_keyboard.default_keyboard_builder(
                                    text = ['📝Оформить предварительный заказ','🛒Корзина','🧾Заказы','⚙️Помощь','🆕Подключить получение результатов'],
                                    sizes = [1,2,1,1],
                                    input_field_placeholder = 'Выберите пункт меню...',
                                    resize_keyboard = True
                                )
                            )
    else: await message.answer('Ошибка! Вы не были подключены к услуге.', 
                                reply_markup = await def_keyboard.default_keyboard_builder(
                                    text = ['📝Оформить предварительный заказ','🛒Корзина','🧾Заказы','⚙️Помощь','🆕Подключить получение результатов'],
                                    sizes = [1,2,1,1],
                                    input_field_placeholder = 'Выберите пункт меню...',
                                    resize_keyboard = True
                                )
                            )
# обработка ввода с клавиатуры пользователя и нажатие кнопок
@router.message(MessageMatch(['корзина', 'корзинка', 'cart']))
async def cart(message: Message) -> None:
    # cart = await request.get_cart(message.from_user.id)
    out_text, keyboard = await order_cart_keyboard.get_cart_buttons(message.from_user.id, message_cart = True)
    if keyboard:
        await message.answer(f'<b>Ваш заказ:</b>\n{out_text}', parse_mode = 'HTML', reply_markup = keyboard)
    else:
        await message.answer('<i><b>Корзина пуста.</b></i>\n\nЧтобы добавить исследование или медицинскую услугу в корзину, нажмите кнопку в меню <b>"Оформить предварительный заказ"</b>.',
                                parse_mode = 'HTML'
                            )

# обработка ввода с клавиатуры пользователя и нажатие кнопок (выводит список заказов)
@router.message(MessageMatch(['посмотреть заказ','мой заказ','заказы','мои заказы', 'история заказов']))
async def orders(message: MessageMatch) -> None:
    page = 1
    count, orders_dict = await funcs.orders(message.from_user.id)
    if orders_dict:
        pages_count = len(orders_dict)
        keyboards = await orders_pagination(orders_dict, int(page), int(pages_count))
        if count  ==  1: t = 'Ваш заказ'
        else: t = 'Ваши заказы'
        await message.answer(f'{t} ({count}):', reply_markup = keyboards)
    else: await message.answer(f'''Вы пока не оформляли заказы.\n
Чтобы оформить заказ, вам необходимо нажать на кнопку <b>"Оформить предварительный заказ"</b>, либо <b>"Корзина"</b>.''', 
parse_mode = 'HTML')
