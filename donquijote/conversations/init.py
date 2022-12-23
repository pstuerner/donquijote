from datetime import datetime as dt

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import ContextTypes, ConversationHandler

from donquijote.conversations.helpers import send
from donquijote.db.mongodb import User
from donquijote.util.util import int_cast, time_cast

user = User()
AGREE, NAME, WORDS_PER_DAY, REMINDER, HOW_OFTEN, WHAT_TIME = range(6)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Function that starts the conversation.

    Args:
        update (telegram._update.Update): The update object
        context (telegram.ext._callbackcontext.CallbackContext): The callback context

    Returns:
        0, to proceed to the AGREE step of the conversation.
    """
    reply_keyboard = [["Yes", "No"]]

    await send(update, "¿Qué pasa, tío?")
    await send(
        update,
        "I'm Don Quijote and I want to help you to master your Spanish!",
    )
    await send(
        update,
        f"Here's how we're going to do it. In the end, to learn a language, it's not really "
        f"about how many words you know, but rather **which** words you know. Apparently, complete fluency is "
        f"in the 10,000 word range, however, you're not required to know all of these words to have a "
        f"conversation. That's why I'm here to help you to study the 5000 most common Spanish words!",
    )

    await send(
        update,
        "Sounds exciting? Let me know if you want to study Spanish with me so we can get you started! (yes/no)",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            one_time_keyboard=True,
            input_field_placeholder="Let's study?",
        ),
    )

    return AGREE


async def agree(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Function that checks if the user agrees to learn vocabulary.

    Args:
        update (telegram._update.Update): The update object
        context (telegram.ext._callbackcontext.CallbackContext): The callback context

    Returns:
        0, if the user input was incorrect to return to the AGREE step of the conversation
        -1, if the user doesn't want to learn or is already registered, ends the conversation
        1, if the user wants to learn to proceed to the NAME step of the conversation
    """
    user_info = update.message.from_user
    context.chat_data["user_id"] = user_info["id"]

    if update.message.text.lower() == "yes":
        if user.exists(user_info["id"]):
            user_name = user.find(user_id=user_info["id"])["name"]
            await send(
                update,
                f"¡Hola {user_name}! Looks like we've talked before. Send /settings to view what we've set up before.",
                reply_markup=ReplyKeyboardRemove(),
            )

            return ConversationHandler.END
        else:
            await send(
                update,
                "Awesome! Let's get started. First of all, pick a neat name that I can call you by. "
                "Simply type it in the chat now.",
                reply_markup=ReplyKeyboardRemove(),
            )

            return NAME
    elif update.message.text.lower() == "no":
        await send(
            update,
            "That's sad to hear! Send /start whenever you want to try again.",
        )

        return ConversationHandler.END
    else:
        await send(
            update,
            "Oops. Somethings wrong with your input. Answer either yes or no.",
        )

        return AGREE


async def name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Function that lets the user input a name.

    Args:
        update (telegram._update.Update): The update object
        context (telegram.ext._callbackcontext.CallbackContext): The callback context

    Returns:
        2, to proceed to the WORDS_PER_DAY step of the conversation
    """
    user_info = update.message.from_user
    name = update.message.text.strip()
    context.chat_data["name"] = name

    user.insert(
        user_id=user_info["id"],
        name=name,
        n_words=None,
        reminder=[],
        sign_up=dt.now(),
    )

    await send(update, f"Sounds good. I'll call you {name} from now on.")
    await send(
        update,
        f"How many new words do you want to practice per day? I'd recommend to learn about five to ten words a day.",
    )

    return WORDS_PER_DAY


async def words_per_day(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Function that lets the user define the amount of new words per day.

    Args:
        update (telegram._update.Update): The update object
        context (telegram.ext._callbackcontext.CallbackContext): The callback context

    Returns:
        2, if the user input was incorrect to return to the WORDS_PER_DAY step of the conversation
        3, to proceed to the REMINDER step of the conversation
    """
    choice = int_cast(update.message.text)

    if choice is None:
        await send(
            update,
            "Oops. Something's wrong with your input. Please make sure to send me a number, e.g. 5.",
        )

        return WORDS_PER_DAY

    context.chat_data["n_words"] = choice
    user.update(
        user_id=context.chat_data["user_id"],
        update_dict={"$set": {"n_words": choice}},
    )

    reply_keyboard = [["Yes", "No"]]

    await send(update, f"{choice} words a day - perfect choice!")
    await send(
        update,
        f"Depending on your learning progress it's possible that some days have more vocabularies than others. "
        f"It's useful to restrict the maximum number of vocabularies per day to avoid learning too many words at the same time. "
        f"I've set the maximum number of words to 30 for now, but you can change this in your settings after the initial setup.",
    )
    await send(
        update,
        f"Now, let's take care of your learning schedule. I can send you a reminder up to three times a day "
        f"so you won't forget to study your vocabularies. Do you want me to send you reminders? (Yes/No)",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            input_field_placeholder="Let's study?",
        ),
    )

    return REMINDER


async def reminder(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Function that lets the set up a learning schedule.

    Args:
        update (telegram._update.Update): The update object
        context (telegram.ext._callbackcontext.CallbackContext): The callback context

    Returns:
        -1, if the user doesn't want to set up a learning schedule, ends the conversation
        3, if the user input was incorrect to return to the REMINDER step of the conversation
        4, to proceed to the HOW_OFTEN step of the conversation
    """
    if update.message.text.lower() == "yes":
        context.chat_data["reminder"] = True
        await send(
            update,
            "Great! How often do you want to practice on a single day?",
            reply_markup=ReplyKeyboardMarkup(
                [["1x", "2x", "3x"]],
                input_field_placeholder="Study frequency",
            ),
        )

        return HOW_OFTEN
    elif update.message.text.lower() == "no":
        context.chat_data["reminder"] = []

        await send(
            update,
            "Okay, not a problem! Simply come back whenenver you want and send /play to practice.",
            reply_markup=ReplyKeyboardRemove(),
        )

        return ConversationHandler.END
    else:
        await send(
            update,
            "Oops. Somethings wrong with your input. Answer either yes or no.",
        )

        return REMINDER


async def how_often(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Function that lets the user define the number of reminders.

    Args:
        update (telegram._update.Update): The update object
        context (telegram.ext._callbackcontext.CallbackContext): The callback context

    Returns:
        4, if the user input was incorrect to return to the HOW_OFTEN step of the conversation
        5, to proceed to the WHAT_TIME step of the conversation
    """
    choice = update.message.text
    freq_dict = {"1x": 1, "2x": 2, "3x": 3}

    if choice not in freq_dict.keys():
        await send(
            update,
            "Oops. Somethings wrong with your input. Answer either 1x, 2x or 3x.",
        )

        return HOW_OFTEN

    context.chat_data["freq"] = freq_dict[choice]
    context.chat_data["current_i"] = 0
    context.chat_data["max_i"] = freq_dict[choice] - 1

    await send(
        update,
        f"Got that. I'll remind you {freq_dict[choice]} {'time' if choice=='1x' else 'times'}. "
        f"At what time to you want me to remind you? Pick a time for each reminder!",
        reply_markup=ReplyKeyboardRemove(),
    )
    await send(update, f"What about your first reminder?")

    return WHAT_TIME


async def what_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Function that lets the user define the reminder times.

    Args:
        update (telegram._update.Update): The update object
        context (telegram.ext._callbackcontext.CallbackContext): The callback context

    Returns:
        -1, if everything is finished, terminates the conversation
        5, if the user input was incorrect or if there's another reminder that must be set
            to return to the WHAT_TIME step of the conversation
    """
    user_info = update.message.from_user
    choice = update.message.text.strip()

    if not time_cast(choice):
        await send(
            update,
            "Oops. Somethings wrong with your input. Make sure that your time format meets HH:MM, e.g. 13:30.",
        )

        return WHAT_TIME

    str_dict = {0: "first", 1: "second", 2: "third"}

    user.update(
        user_id=user_info["id"], update_dict={"$push": {"reminder": choice}}
    )
    await send(
        update,
        f"Okay. I'll remind you the {str_dict[context.chat_data['current_i']]} time at {choice}",
    )

    if context.chat_data["current_i"] + 1 > context.chat_data["max_i"]:
        await send(
            update,
            f"That's it! You're good to go. I will send you a reminder as soon as we hit one of the alarms you just set.",
        )
        await send(
            update,
            f"However, you can learn at any time you want! Simply send /play and I'll provide you with the ",
        )
        return ConversationHandler.END
    else:
        context.chat_data["current_i"] += 1
        await send(
            update,
            f"What about your {str_dict[context.chat_data['current_i']]} reminder?",
        )
        return WHAT_TIME
