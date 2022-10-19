from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler

from donquijote.conversations.init import REMINDER
from donquijote.db.mongodb import User
from donquijote.util.util import int_cast

user = User()
SETTINGS_ROUTER = 0
CHANGE_NAME = 1
CHANGE_WORDS = 6
CHANGE_MAX_VOCABS = 7


async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_info = update.message.from_user
    reply_keyboard = [["Name", "Reminder"], ["Words A Day", "Max Vocabs"]]

    if not user.exists(user_id=user_info["id"]):
        await update.message.reply_text(
            f"¡Hola! You're not a registered. Send /start so we can register you."
        )

    await update.message.reply_text(
        f"You can change your name, deactivate/set your reminders or change the number of words to learn per day.",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            input_field_placeholder="Change settings",
        ),
    )

    return SETTINGS_ROUTER


async def settings_router(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    user_info = update.message.from_user
    choice = update.message.text

    if choice == "Name":
        await update.message.reply_text(
            f"Alright, then pick a new name! Just send it to me in the chat."
        )

        return CHANGE_NAME
    elif choice == "Reminder":
        reply_keyboard = [["Yes", "No"]]
        user.update(
            user_id=user_info["id"], update_dict={"$set": {"reminder": []}}
        )
        await update.message.reply_text(
            f"Let's set up your new learning schedule. Do you want to receive any reminders? (Yes/No)",
            reply_markup=ReplyKeyboardMarkup(
                reply_keyboard,
                input_field_placeholder="Let's study?",
            ),
        )

        return REMINDER
    elif choice == "Words A Day":
        await update.message.reply_text(
            f"Okay, how many words do you want to learn per day?"
        )

        return CHANGE_WORDS
    elif choice == "Max Vocabs":
        await update.message.reply_text(
            f"Okay, what's the maximum amount of vocabularies you want to learn on a single day?"
        )

        return CHANGE_MAX_VOCABS
    else:
        await update.message.reply_text(
            "Oops. Somethings wrong with your input. Send one of the following responses: 'Name', 'Reminder', 'Words A Day', 'Max Vocabs'."
        )

        return SETTINGS_ROUTER


async def change_name(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    user_info = update.message.from_user

    user.update(
        user_id=user_info["id"],
        update_dict={"$set": {"name": update.message.text.strip()}},
    )

    await update.message.reply_text(
        f"Okay, I'll call you {update.message.text} from now on."
    )

    return ConversationHandler.END


async def change_words(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    user_info = update.message.from_user
    choice = int_cast(update.message.text)

    if choice is None:
        await update.message.reply_text(
            "Oops. Something's wrong with your input. Please make sure to send me a number, e.g. 5."
        )

        return CHANGE_WORDS

    user.update(
        user_id=user_info["id"],
        update_dict={"$set": {"n_words": choice}},
    )

    await update.message.reply_text(
        f"Okay, I'll send you {choice} from now on."
    )

    return ConversationHandler.END


async def change_max_vocabs(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    user_info = update.message.from_user
    choice = int_cast(update.message.text)

    if choice is None:
        await update.message.reply_text(
            "Oops. Something's wrong with your input. Please make sure to send me a number, e.g. 20."
        )

        return CHANGE_MAX_VOCABS

    user.update(
        user_id=user_info["id"],
        update_dict={"$set": {"max_vocabs": choice}},
    )

    await update.message.reply_text(
        f"Okay, I'll send you not more than {choice} vocabularies on a single day."
    )

    return ConversationHandler.END
