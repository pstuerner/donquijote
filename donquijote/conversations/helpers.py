import time


async def send(update, txt, reply_markup=None):
    while True:
        try:
            return await update.message.reply_text(
                txt,
                reply_markup=reply_markup,
                read_timeout=30,
                write_timeout=30,
            )
        except Exception:
            time.sleep(3)


async def edit_message_text(context):
    while True:
        try:
            return await context.bot.edit_message_text(
                chat_id=context.chat_data["chat_id"],
                message_id=context.chat_data["message_id"],
                text=context.chat_data["new_message"],
            )
        except Exception:
            time.sleep(3)
