import logging
import logging.handlers
import asyncio
import os
from discord.ext import commands
import discord

from cogs.music import Music


async def main():
    # Discord bot logging configuration
    # See more here: https://docs.python.org/3/library/logging.html
    logger = logging.getLogger("discord")
    logger.setLevel(logging.DEBUG)
    handler = logging.handlers.RotatingFileHandler(
        filename="discord-lib.log",
        encoding="utf-8",
        maxBytes=32 * 1024 * 1024,  # 32 MiB
        backupCount=5,
    )
    handler.setFormatter(
        logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s")
    )
    logger.addHandler(handler)

    # Discord bot intents
    # See more here: https://discordpy.readthedocs.io/en/stable/api.html?highlight=intents#intents
    intents = discord.Intents.default()
    intents.message_content = True

    bot = commands.Bot(
        intents=intents,
        command_prefix=commands.when_mentioned_or("!"),
        description="A bot representing NYS's late Governor Andy Cuomo",
    )

    await bot.load_extension("cogs.music")
    await bot.start(os.getenv("DISCORD_TOKEN", ""))


asyncio.run(main())
