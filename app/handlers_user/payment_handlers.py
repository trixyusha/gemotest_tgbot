import os

from aiogram import F
from aiogram.types import Message, CallbackQuery
from aiogram.types import LabeledPrice, PreCheckoutQuery
from aiogram.types.input_file import BufferedInputFile as send_buffer
from app.database.requests.order_requests import place_order
from app.keyboards_user.default_keyboard import default_keyboard_builder
from app.keyboards_user.inline.order_cart_keyboard import get_cart_buttons

from app.handlers_user.main_handlers import router
from .main_handlers import GET_QR_TEXT, GET_QR_TEXT_CONNECT


# пользователь выбрал оплату в лабораторном отделении
@router.callback_query(F.data.startswith('offline_payment'))
async def offline_payment(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text('Вы выбрали оплату в лабораторном отделении.', reply_markup = None)
    data = callback.data.split('#')[1]
    order_num = data.split('/')[0]
    anon = data.split('/')[1]
    qr_buffer = await place_order(callback.from_user.id, order_num, False, anon)
    if qr_buffer:
        await callback.message.answer_photo(photo = send_buffer(qr_buffer.getvalue(), f'qrcode_{callback.from_user.id}.png'), 
                                                caption = GET_QR_TEXT, 
                                                protect_content = True, parse_mode = 'HTML'
                                            )
    else:
        # сделать проверку на подключение мед. карты клиента, иначе отправить новый QR
        await callback.message.edit_text('Воспользуйтесь своим QR-кодом, который уже был отправлен в этот чат, чтобы отсканировать в терминале самообслуживания или у администратора.', 
                                            reply_markup = await default_keyboard_builder(
                                            text = 'Запросить QR-код',
                                            callback_data = f'resend_qrcode',
                                            sizes = 1
                                        ))

# выбрана онлайн оплата
@router.callback_query(F.data.startswith('online_payment'))
async def online_payment(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text('Вы выбрали онлайн оплату.', reply_markup = None)
    # добавить в бд заказ (перенести из корзины в заказы)
    data = callback.data.split('#')[1]
    order_num = data.split('/')[0]
    anon = data.split('/')[1]
    cost = await get_cart_buttons(callback.from_user.id, True)
    price = LabeledPrice(label = f'Заказ №{order_num}', amount = cost*100)
    await callback.message.answer_invoice(
        title = f'Заказ №{order_num}',
        description = f'Оплата предварительного заказа №{order_num}. В течение 30 дней, с момента оформления заказа, вам необходимо посетить любое лабораторное отделение.',
        provider_token = os.getenv('PAYMENTS_TOKEN'),
        payload = f'place_an_order#{order_num}/{anon}',
        currency = 'rub',
        prices = [price],
        start_parameter = 'GemotestBot',
        provider_data = None,
        need_name = False,
        need_phone_number = False,
        need_email = False, # точно нужна почта?
        need_shipping_address = False,
        is_flexible = False,
        disable_notification = False,
        protect_content = True,
        reply_to_message_id = None,
        reply_markup = None
    )

@router.pre_checkout_query(lambda query: True)
async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.answer(ok = True)
    print(pre_checkout_query)

@router.message(F.successful_payment)
async def success_payment(message: Message):
    data = message.successful_payment.invoice_payload.split('#')[1]
    order_num = data.split('/')[0]
    anon = data.split('/')[1]
    qr_buffer = await place_order(message.from_user.id, order_num, True, anon)
    if qr_buffer:
        await message.answer_photo(photo = send_buffer(qr_buffer.getvalue(), f'qrcode_{message.from_user.id}.png'), 
                                        caption = 'Это ваш QR-код (карточка клиента).\nОтсканируйте его в терминале самообслуживания или у администратора.', 
                                        protect_content = True
                                    )
    else:
        await message.answer('Воспользуйтесь своим QR-кодом, который уже был отправлен в этот чат, чтобы отсканировать в терминале самообслуживания или у администратора.',
                                reply_markup = await default_keyboard_builder(
                                    text = 'Запросить QR-код',
                                    callback_data = f'resend_qrcode#{order_num}',
                                    sizes = 1
                                )
                            )
        
@router.callback_query(F.data.startswith('resend_qrcode'))
async def resend_qrcode(callback: CallbackQuery):
    await callback.answer()
    qr_buffer = await place_order(callback.from_user.id)
    await callback.message.edit_text('Вы запросили повторную отправку QR-кода.', reply_markup = None)
    await callback.message.answer_photo(photo = send_buffer(qr_buffer.getvalue(), f'qrcode_{callback.from_user.id}.png'), 
                                            caption = GET_QR_TEXT_CONNECT, 
                                            protect_content = True, parse_mode = 'HTML'
                                        )

