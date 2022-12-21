from telegram import ReplyKeyboardRemove, Update
from telegram.ext import ContextTypes, ConversationHandler

from donquijote.conversations.helpers import send


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    await send(
        update,
        "Bye! I hope we can talk again some day.",
        reply_markup=ReplyKeyboardRemove(),
    )

    return ConversationHandler.END
