import random
from datetime import datetime as dt
from datetime import timedelta as td

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from donquijote.db.mongodb import SRS, Practice, User, Vocabulary
from donquijote.util.const import FAILURE, INT_EMOJI_DICT, SRS_DICT, SUCCESS

user = User()
vocabulary = Vocabulary()
practice = Practice()
srs = SRS()


async def play(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_info = update.message.from_user
    context.chat_data["chat_id"] = None
    context.chat_data["message_id"] = None
    context.chat_data["new_message"] = None

    if not user.exists(user_id=user_info["id"]):
        await update.message.reply_text(
            f"¡Hola! You're not a registered. Send /start so we can register you.",
            write_timeout=10,
        )

        return ConversationHandler.END
    else:
        u = user.find(user_id=user_info["id"])

    if not practice.exists(user_id=u["user_id"], timestamp=dt.now()):
        vocabs = []
        srs_repeat = list(
            srs.repeat(
                user_id=user_info["id"],
                timestamp=dt.now().replace(
                    hour=0, minute=0, second=0, microsecond=0
                ),
            )
        )
        if len(srs_repeat) > 0:
            vocab_list = [x["vocab_id"] for x in srs_repeat]
            vocabs += list(vocabulary.from_vocab_list(vocab_list=vocab_list))

        vocabs += list(vocabulary.sample(n_words=int(u["n_words"])))

        for vocab in vocabs:
            if not srs.exists(
                user_id=u["user_id"], vocab_id=vocab["vocab_id"]
            ):
                srs.insert(user_id=u["user_id"], vocab_id=vocab["vocab_id"])
    else:
        p = practice.find(user_id=u["user_id"], timestamp=dt.now())
        vocabs = list(vocabulary.from_vocab_list(vocab_list=p["vocabs"]))

    random.shuffle(vocabs)

    practice_id = practice.max_id() + 1
    practice.insert(
        practice_id=practice_id,
        user_id=u["user_id"],
        timestamp=dt.now(),
        vocabs=[v["vocab_id"] for v in vocabs],
    )
    context.chat_data["vocabs"] = [{**v, **{"attempts": 0}} for v in vocabs]
    context.chat_data["practice_id"] = practice_id

    await update.message.reply_text(
        f"¡Vamos! You have {len(vocabs)} words to study for today.",
        write_timeout=10,
    )
    await update.message.reply_text(
        f'{vocabs[0]["en"]}\n----------\n{vocabs[0]["sentence-en"]}',
        write_timeout=10,
    )

    return 0


def progress(srs_item, attempts):
    srs_item["last_learn"] = dt.now()

    if attempts == 1:
        if srs_item["quick_repeat"]:
            srs_item["quick_repeat"] = False
        else:
            srs_item["level"] += 1

        if srs_item["level"] < 5:
            srs_item["next_learn"] = srs_item["last_learn"].replace(
                hour=0, minute=0, second=0, microsecond=0
            ) + td(days=SRS_DICT[srs_item["level"]])
        else:
            srs_item["next_learn"] = dt(2099, 1, 1)
    else:
        srs_item["next_learn"] = srs_item["last_learn"].replace(
            hour=0, minute=0, second=0, microsecond=0
        ) + td(days=1)

        if srs_item["level"] > 1:
            srs_item["level"] -= 1
            srs_item["quick_repeat"] = True
        else:
            srs_item["quick_repeat"] = False

    return srs_item


async def vocab(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if len(context.chat_data["vocabs"]) > 0:
        user_info = update.message.from_user
        if context.chat_data["message_id"]:
            await context.bot.edit_message_text(
                chat_id=context.chat_data["chat_id"],
                message_id=context.chat_data["message_id"],
                text=context.chat_data["new_message"],
            )
        context.chat_data["vocabs"][0]["attempts"] += 1
        vocab = context.chat_data["vocabs"][0]
        practice.update(
            practice_id=context.chat_data["practice_id"],
            update_dict={
                "$set": {f"attempts.{vocab['vocab_id']}": vocab["attempts"]}
            },
        )
        context.chat_data["vocabs"].pop(0)
        reply = update.message.text

        if reply.strip().lower() == vocab["sp"].strip().lower():
            context.chat_data["chat_id"] = None
            context.chat_data["message_id"] = None
            context.chat_data["new_message"] = None
            await update.message.reply_text(
                f"{random.choice(SUCCESS)}\n----------\n{vocab['sentence-sp']}",
                write_timeout=10,
            )
        else:
            failure_msg = random.choice(FAILURE)
            correction = await update.message.reply_text(
                f"{failure_msg.format(sp=vocab['sp'])}\n----------\n{vocab['sentence-sp']}",
                write_timeout=10,
            )
            context.chat_data["chat_id"] = correction.chat_id
            context.chat_data["message_id"] = correction.message_id
            context.chat_data["new_message"] = failure_msg.format(
                sp="_________"
            )
            context.chat_data["vocabs"].append(vocab)

    if len(context.chat_data["vocabs"]) > 0:
        await update.message.reply_text(
            f'{context.chat_data["vocabs"][0]["en"]}\n----------\n{context.chat_data["vocabs"][0]["sentence-en"]}',
            write_timeout=10,
        )
        return 0
    else:
        if (
            practice.exists(
                user_id=user_info["id"], timestamp=dt.now(), return_count=True
            )
            == 1
        ):
            upgrades, downgrades, remains = [], [], []
            attempts = practice.find(
                user_id=user_info["id"], timestamp=dt.now()
            )["attempts"]
            for v, a in attempts.items():
                srs_item = srs.find(user_id=user_info["id"], vocab_id=int(v))
                srs_update = {
                    "level_pre": srs_item["level"],
                    "level_post": None,
                    "vocab": vocabulary.find(vocab_id=int(v)),
                }
                srs_item = progress(srs_item, a)
                srs_update["level_post"] = srs_item["level"]
                srs.update(
                    user_id=user_info["id"],
                    vocab_id=int(v),
                    update_dict={"$set": srs_item},
                )

                if srs_update["level_post"] > srs_update["level_pre"]:
                    upgrades.append(srs_update)
                elif srs_update["level_post"] < srs_update["level_pre"]:
                    downgrades.append(srs_update)
                else:
                    remains.append(srs_update)

            await update.message.reply_text(
                f"Awesome! You've just finished learning your words. Here are your stats.",
                write_timeout=10,
            )

            upgrades_str = "✨ Upgrades ✨\n" + "\n".join(
                [
                    f"{u['vocab']['en']} -> {u['vocab']['sp']}: {INT_EMOJI_DICT[u['level_pre']]} -> {INT_EMOJI_DICT[u['level_post']]}"
                    for u in upgrades
                ]
            )
            downgrades_str = "😭 Downgrades 😭\n" + "\n".join(
                [
                    f"{d['vocab']['en']} -> {d['vocab']['sp']}: {INT_EMOJI_DICT[d['level_pre']]} -> {INT_EMOJI_DICT[d['level_post']]}"
                    for d in downgrades
                ]
            )
            remains_str = "😑 Remains 😑\n" + "\n".join(
                [
                    f"{r['vocab']['en']} -> {r['vocab']['sp']}: {INT_EMOJI_DICT[r['level_pre']]} -> {INT_EMOJI_DICT[r['level_post']]}"
                    for r in remains
                ]
            )

            if len(upgrades) > 0:
                await update.message.reply_text(upgrades_str, write_timeout=10)
            if len(downgrades) > 0:
                await update.message.reply_text(
                    downgrades_str, write_timeout=10
                )
            if len(remains) > 0:
                await update.message.reply_text(remains_str, write_timeout=10)
        else:
            await update.message.reply_text(
                f"Awesome! You've just finished learning your words. See you soon 😇.",
                write_timeout=10,
            )

        return ConversationHandler.END


async def counts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    vocab = context.chat_data["vocabs"].pop(-1)
    await update.message.reply_text(
        f'Typo? Not a problem. I marked your last answer for "{vocab["en"]}" as correct!',
        write_timeout=10,
    )

    return 0
