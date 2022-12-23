import random

from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler

from donquijote.conversations.helpers import edit_message_text, send
from donquijote.db.mongodb import SRS, Practice, User, Vocabulary
from donquijote.util.const import FAILURE, INT_EMOJI_DICT, SRS_DICT, SUCCESS

ABBRS_MAPPING = {
    "noun: fem": "nf",
    "noun: masc": "nm",
    "verb": "v",
    "adjective": "adj",
    "adverb": "adv",
    "noun masc/fem": "nmf",
    "noun: common": "nc",
    "pronoun": "pron",
    "number": "num",
    "preposition": "prep",
    "conjunction": "conj",
    "noun: masc/fem, msc given": "nm/f",
    "interjection": "interj",
    "article": "art",
    "neuter": "n",
}

vocabulary = Vocabulary()


def type_cast(inp):
    """A helper function that helps to cast a number range (e.g. 10-20) to
    acutal integers.

    Args:
        inp (str): The range string input, e.g. 10-20

    Returns:
        list: lower and upper bound or
        None: if the format is wrong
    """
    try:
        range = [int(x) for x in inp.replace(" ", "").split("-")]
    except Exception:
        return None

    if len(range) != 2:
        return None
    elif any([range[0] < 0, range[1] < 0]):
        return None
    elif range[1] <= range[0]:
        return None
    else:
        return range


async def learn(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Function that starts the learn conversation flow. This conversation lets
    the user pick a group of words (e.g. verbs, adjectives, nouns) and a range (e.g. 0-100)
    to select a set of vocabulary to learn. The range defines the frequency of the words,
    meaning that lower ranges (e.g. 0-10) stand for more frequently used words.

    Args:
        update (telegram._update.Update): The update object
        context (telegram.ext._callbackcontext.CallbackContext): The callback context

    Returns:
        0, to proceed to the which_word_group step of the conversation.
    """
    reply_keyboard = [
        list(ABBRS_MAPPING.keys())[i : i + 2]
        for i in range(0, len(ABBRS_MAPPING), 2)
    ]

    await send(
        update,
        "Let's learn! Which group of words do you want to study?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard,
            one_time_keyboard=True,
            input_field_placeholder="Let's study?",
        ),
    )

    return 0


async def which_word_group(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Function that lets the user pick a word group.

    Args:
        update (telegram._update.Update): The update object
        context (telegram.ext._callbackcontext.CallbackContext): The callback context

    Returns:
        1, to proceed to the which_word_range step of the conversation.
    """
    group = update.message.text.lower()
    if group not in list(ABBRS_MAPPING.keys()):
        await send(
            update,
            f"I'm sorry, but I don't understand. Send me one of the following word groups: {', '.join(list(ABBRS_MAPPING.keys()))}.",
        )

        return 0
    else:
        context.chat_data["word_group"] = group
        vocab_count = vocabulary.vocab_count(abbr=ABBRS_MAPPING[group])
        context.chat_data["vocab_count"] = vocab_count
        await send(
            update,
            f"Great! Let's learn some {group}. Define a range of words you want to learn, e.g. 0-10. Lower numbers "
            f"indicate more important words. For example, if you want to learn the 20 most important {group} send 0-20. "
            f"There are a total of {vocab_count} words, so every number between 0 and {vocab_count-1} works 😇.",
        )

        return 1


async def which_word_range(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Function that lets the user pick a frequency range.

    Args:
        update (telegram._update.Update): The update object
        context (telegram.ext._callbackcontext.CallbackContext): The callback context

    Returns:
        1, to return to the which_word_range step of the conversation if the user input was wrong
        2, to proceed to the play_learn part of the conversation
    """
    range = type_cast(update.message.text)

    if not range or range[1] >= context.chat_data["vocab_count"]:
        await send(
            update,
            f"Something went wrong! Make sure that your range format is correct, e.g. 0-20, and that your end range is within the total number of words ({context.chat_data['vocab_count']-1}).",
        )

        return 1

    vocabs = vocabulary.range(
        start=range[0],
        end=range[1],
        abbr=ABBRS_MAPPING[context.chat_data["word_group"]],
    )
    context.chat_data["vocabs"] = [{**v, **{"attempts": 0}} for v in vocabs]
    context.chat_data["vocabs_done"] = []

    await send(
        update,
        f"Awesome. Let's learn {context.chat_data['word_group']}, words {range[0]} to {range[1]}.",
    )
    await send(
        update,
        f'{context.chat_data["vocabs"][0]["en"]}\n----------\n{context.chat_data["vocabs"][0]["sentence-en"]}',
    )

    return 2


async def play_learn(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Function that sends the user English words, waits for a Spanish response, and
    checks if the answer is correct as long as all words have been guessed correctly.

    Args:
        update (telegram._update.Update): The update object
        context (telegram.ext._callbackcontext.CallbackContext): The callback context

    Returns:
        -1, if everything is finished, ends the conversation
        2, to return to the play_learn part of the conversation
    """
    if len(context.chat_data["vocabs"]) > 0:
        if context.chat_data.get("message_id", None):
            await edit_message_text(context)
        context.chat_data["vocabs"][0]["attempts"] += 1
        vocab = context.chat_data["vocabs"][0]
        context.chat_data["vocabs"].pop(0)
        reply = update.message.text

        if reply.strip().lower() == vocab["sp"].strip().lower():
            context.chat_data["chat_id"] = None
            context.chat_data["message_id"] = None
            context.chat_data["new_message"] = None
            context.chat_data["vocabs_done"].append(vocab)
            await send(
                update,
                f"{random.choice(SUCCESS)}\n----------\n{vocab['sentence-sp']}",
            )
        else:
            failure_msg = random.choice(FAILURE)
            correction = await send(
                update,
                f"{failure_msg.format(sp=vocab['sp'])}\n----------\n{vocab['sentence-sp']}",
            )
            context.chat_data["chat_id"] = correction.chat_id
            context.chat_data["message_id"] = correction.message_id
            context.chat_data["new_message"] = failure_msg.format(
                sp="_________"
            )
            context.chat_data["vocabs"].append(vocab)

    if len(context.chat_data["vocabs"]) > 0:
        await send(
            update,
            f'{context.chat_data["vocabs"][0]["en"]}\n----------\n{context.chat_data["vocabs"][0]["sentence-en"]}',
        )
        return 2
    else:
        await send(
            update,
            f"Awesome! You've just finished learning your words. Here are your stats.",
        )

        perfect = [
            v for v in context.chat_data["vocabs_done"] if v["attempts"] == 1
        ]
        improvement = sorted(
            [v for v in context.chat_data["vocabs_done"] if v["attempts"] > 1],
            key=lambda f: -f["attempts"],
        )

        perfect_str = "✨ Perfect ✨\n" + "\n".join(
            [f"{u['en']} -> {u['sp']}" for u in perfect]
        )
        improvement_str = "😭 Improvement 😭\n" + "\n".join(
            [f"{u['attempts']}x: {u['en']} -> {u['sp']}" for u in improvement]
        )

        if len(perfect) > 0:
            await send(update, perfect_str)
        if len(improvement) > 0:
            await send(update, improvement_str)

    return ConversationHandler.END
