from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder



async def default_keyboard_builder(
    text: str | list[str], 
    callback_data: str | list[str] = None, 
    sizes: int | list[int] = 2,
    request_cont: bool = False,
    **kwargs) -> InlineKeyboardBuilder | ReplyKeyboardBuilder:
    if callback_data:
        builder = InlineKeyboardBuilder()
        # builder.as_markup(resize_keyboard = True)
    else:
        builder = ReplyKeyboardBuilder()
    if isinstance(text, str):
        text = [text]
    if callback_data and isinstance(callback_data, str):
        callback_data = [callback_data]
    if isinstance(sizes, int):
        sizes = [sizes]
    if isinstance(builder, InlineKeyboardBuilder):
        [builder.button(text = txt, callback_data = cbd) for txt, cbd in zip(text, callback_data)]
    else:
        if request_cont:
            [builder.button(text = txt, request_contact = request_cont) for txt in text]
        else: [builder.button(text = txt) for txt in text]
    builder.adjust(*sizes)
    return builder.as_markup(**kwargs)
