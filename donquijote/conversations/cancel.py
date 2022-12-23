from telegram import ReplyKeyboardRemove, Update
from telegram.ext import ContextTypes, ConversationHandler

from donquijote.conversations.helpers import send


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Function to cancel and end the conversation.

    Args:
        update (telegram._update.Update): The update object
        context (telegram.ext._callbackcontext.CallbackContext): The callback context

    Returns:
        -1, ends the conversation handler

    """
    await send(
        update,
        "Bye! I hope we can talk again some day.",
        reply_markup=ReplyKeyboardRemove(),
    )

    return ConversationHandler.END
