import time


async def send(update, txt, reply_markup=None):
    """Helper function that wraps the python-telegram-bot reply_text funcionality
    into a while loop with a try/except catch. This is not pretty but helps to prevent
    that Telegram timeouts force the bot to get stuck in mid conversation.

    Args:
        update (telegram._update.Update): The update object
        txt (str): The text message to send
        reply_markup (telegram._replykeyboardmarkup.ReplyKeyboardMarkup): A reply keyboard
            that allows the user to push buttons inside the app (default: None)

    Returns:
        None. Sends the message.

    """
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
    """Helper function that wraps the python-telegram-bot edit_message_text function
    into an endless loop with a try/except catch phrase to avoit Telegram timeouts to force
    the bot into getting stuck mid conversation.

    Args:
        context (telegram.ext._callbackcontext.CallbackContext): The callback context

    Returns:
        None. Edits the already sent text message.
    """
    while True:
        try:
            return await context.bot.edit_message_text(
                chat_id=context.chat_data["chat_id"],
                message_id=context.chat_data["message_id"],
                text=context.chat_data["new_message"],
            )
        except Exception:
            time.sleep(3)
