import asyncio
import os
from datetime import datetime as dt

import pytz
from telegram import Bot

from donquijote.conversations.helpers import send
from donquijote.db.mongodb import User

u = User()
bot = Bot(token=os.environ["BOT_TOKEN"])
loop = asyncio.get_event_loop()


def main():
    """Main entrypoint for the remind bot.

    Args:
        None

    Returns:
        None. Runs an endless loop that continously fetches schedule times
        and checks if a reminder is necessary.
    """
    now = dt.now(pytz.timezone("Europe/Berlin"))
    while True:
        if dt.now().minute != now.minute:
            now = dt.now(pytz.timezone("Europe/Berlin"))
            users = u.find_all()

            for user in users:
                for reminder in user["reminder"]:
                    dt_reminder = dt.strptime(reminder, "%H:%M")
                    if (dt_reminder.hour == now.hour) and (
                        dt_reminder.minute == now.minute
                    ):
                        msg = f"Hola {user['name']}! Es hora de aprender tu vocabulario. Escribe /play y podemos empezar."
                        loop.run_until_complete(
                            send(bot, user["user_id"], msg)
                        )


if __name__ == "__main__":
    main()
