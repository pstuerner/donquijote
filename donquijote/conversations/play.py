import random
from datetime import datetime as dt
from datetime import timedelta as td

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from donquijote.conversations.helpers import edit_message_text, send
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
            f"¡Hola! You're not registered yet. Send /start so we can register you.",
        )

        return ConversationHandler.END
    else:
        u = user.find(user_id=user_info["id"])

    if not practice.exists(user_id=u["user_id"], timestamp=dt.now()):
        vocabs = []
        all_srs = [
            x["vocab_id"]
            for x in srs.col.find(
                {"user_id": u["user_id"]}, {"_id": 0, "vocab_id": 1}
            )
        ]
        srs_repeat = list(
            srs.repeat(
                user_id=u["user_id"],
                timestamp=dt.now().replace(
                    hour=0, minute=0, second=0, microsecond=0
                ),
            )
        )
        if len(srs_repeat) > 0:
            vocab_list = [x["vocab_id"] for x in srs_repeat]
            vocabs += list(vocabulary.from_vocab_list(vocab_list=vocab_list))

        if len(vocabs) < u["n_words"]:
            vocabs += list(
                vocabulary.sample(
                    n_words=u["n_words"] - len(vocabs),
                    nin=all_srs,
                )
            )

        for vocab in vocabs:
            if not srs.exists(
                user_id=u["user_id"], vocab_id=vocab["vocab_id"]
            ):
                srs.insert(user_id=u["user_id"], vocab_id=vocab["vocab_id"])
    else:
        p = practice.find(user_id=u["user_id"], timestamp=dt.now())
        vocabs = list(vocabulary.from_vocab_list(vocab_list=p["vocabs"]))

    random.shuffle(vocabs)

    context.chat_data["practice"] = {
        "practice_id": practice.max_id() + 1,
        "user_id": u["user_id"],
        "timestamp": dt.now(),
        "vocabs": [v["vocab_id"] for v in vocabs],
        "attempts": {str(v["vocab_id"]): 0 for v in vocabs},
    }
    context.chat_data["vocabs"] = vocabs

    await send(
        update, f"¡Vamos! You have {len(vocabs)} words to study for today."
    )
    await send(
        update, f'{vocabs[0]["en"]}\n----------\n{vocabs[0]["sentence-en"]}'
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
        if context.chat_data["message_id"]:
            await edit_message_text(context)
        vocab = context.chat_data["vocabs"][0]
        context.chat_data["practice"]["attempts"][str(vocab["vocab_id"])] += 1
        context.chat_data["vocabs"].pop(0)
        reply = update.message.text

        if reply.strip().lower() == vocab["sp"].strip().lower():
            context.chat_data["chat_id"] = None
            context.chat_data["message_id"] = None
            context.chat_data["new_message"] = None
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
        return 0
    else:
        streak = user.find(context.chat_data["practice"]["user_id"])["streak"]
        if not practice.exists(
            user_id=context.chat_data["practice"]["user_id"],
            timestamp=dt.now(),
        ):
            if practice.exists(
                user_id=context.chat_data["practice"]["user_id"],
                timestamp=dt.now() - td(days=1),
            ):
                streak += 1
            else:
                streak = 1
            user.update(
                context.chat_data["practice"]["user_id"],
                update_dict={"$set": {"streak": streak}},
            )

            upgrades, downgrades, remains = [], [], []
            for v, a in context.chat_data["practice"]["attempts"].items():
                srs_item = srs.find(
                    user_id=context.chat_data["practice"]["user_id"],
                    vocab_id=int(v),
                )
                srs_update = {
                    "level_pre": srs_item["level"],
                    "level_post": None,
                    "vocab": vocabulary.find(vocab_id=int(v)),
                }
                srs_item = progress(srs_item, a)
                srs_update["level_post"] = srs_item["level"]
                srs.update(
                    user_id=context.chat_data["practice"]["user_id"],
                    vocab_id=int(v),
                    update_dict={"$set": srs_item},
                )

                if srs_update["level_post"] > srs_update["level_pre"]:
                    upgrades.append(srs_update)
                elif srs_update["level_post"] < srs_update["level_pre"]:
                    downgrades.append(srs_update)
                else:
                    remains.append(srs_update)

            await send(
                update,
                f"Awesome! You've just finished learning your words. "
                f"You are currently on a {streak} day streak! "
                f"See you soon 😇.",
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
                await send(update, upgrades_str)
            if len(downgrades) > 0:
                await send(update, downgrades_str)
            if len(remains) > 0:
                await send(update, remains_str)
        else:
            await send(
                update,
                f"Awesome! You've just finished learning your words. "
                f"You are currently on a {streak} day streak! "
                f"See you soon 😇.",
            )

        practice.insert(**context.chat_data["practice"])

        return ConversationHandler.END


async def counts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    vocab = context.chat_data["vocabs"].pop(-1)
    await send(
        update,
        f'Typo? Not a problem. I marked your last answer for "{vocab["en"]}" as correct!',
    )

    return 0
