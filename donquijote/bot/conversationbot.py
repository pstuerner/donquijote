import os

from telegram.ext import (
    Application,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from donquijote.conversations.cancel import cancel
from donquijote.conversations.init import (
    AGREE,
    HOW_OFTEN,
    NAME,
    REMINDER,
    WHAT_TIME,
    WORDS_PER_DAY,
    agree,
    how_often,
    name,
    reminder,
    start,
    what_time,
    words_per_day,
)
from donquijote.conversations.learn import (
    learn,
    play_learn,
    which_word_group,
    which_word_range,
)
from donquijote.conversations.play import counts, play, vocab
from donquijote.conversations.settings import (
    CHANGE_MAX_VOCABS,
    CHANGE_NAME,
    CHANGE_WORDS,
    SETTINGS_ROUTER,
    change_max_vocabs,
    change_name,
    change_words,
    settings,
    settings_router,
)


def main() -> None:
    application = Application.builder().token(os.environ["BOT_TOKEN"]).build()

    init_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            AGREE: [MessageHandler(filters.TEXT & (~filters.COMMAND), agree)],
            NAME: [MessageHandler(filters.TEXT & (~filters.COMMAND), name)],
            WORDS_PER_DAY: [
                MessageHandler(
                    filters.TEXT & (~filters.COMMAND), words_per_day
                )
            ],
            REMINDER: [
                MessageHandler(filters.TEXT & (~filters.COMMAND), reminder)
            ],
            HOW_OFTEN: [
                MessageHandler(filters.TEXT & (~filters.COMMAND), how_often)
            ],
            WHAT_TIME: [
                MessageHandler(filters.TEXT & (~filters.COMMAND), what_time)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    play_handler = ConversationHandler(
        entry_points=[CommandHandler("play", play)],
        states={
            0: [
                MessageHandler(filters.TEXT & (~filters.COMMAND), vocab),
                CommandHandler("counts", counts),
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        conversation_timeout=300,
    )

    learn_handler = ConversationHandler(
        entry_points=[CommandHandler("learn", learn)],
        states={
            0: [
                MessageHandler(
                    filters.TEXT & (~filters.COMMAND), which_word_group
                )
            ],
            1: [
                MessageHandler(
                    filters.TEXT & (~filters.COMMAND), which_word_range
                )
            ],
            2: [MessageHandler(filters.TEXT & (~filters.COMMAND), play_learn)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        conversation_timeout=300,
    )

    settings_handler = ConversationHandler(
        entry_points=[CommandHandler("settings", settings)],
        states={
            SETTINGS_ROUTER: [
                MessageHandler(
                    filters.TEXT & (~filters.COMMAND), settings_router
                )
            ],
            CHANGE_NAME: [
                MessageHandler(filters.TEXT & (~filters.COMMAND), change_name)
            ],
            REMINDER: [
                MessageHandler(filters.TEXT & (~filters.COMMAND), reminder)
            ],
            HOW_OFTEN: [
                MessageHandler(filters.TEXT & (~filters.COMMAND), how_often)
            ],
            WHAT_TIME: [
                MessageHandler(filters.TEXT & (~filters.COMMAND), what_time)
            ],
            CHANGE_WORDS: [
                MessageHandler(filters.TEXT & (~filters.COMMAND), change_words)
            ],
            CHANGE_MAX_VOCABS: [
                MessageHandler(
                    filters.TEXT & (~filters.COMMAND), change_max_vocabs
                )
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(play_handler)
    application.add_handler(learn_handler)
    application.add_handler(init_handler)
    application.add_handler(settings_handler)

    application.run_polling(timeout=120)


if __name__ == "__main__":
    main()
