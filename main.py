import logging
import logging.handlers
import asyncio
import os
from typing import List, Optional
from discord.ext import commands
import discord

from lib.data.tiny import get_db_from_s3


class AndyBot(commands.Bot):
    def __init__(
        self,
        *args,
        initial_extensions: List[str],
        db_name: Optional[str] = None,
        testing_guild_id: Optional[int] = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.db_name = db_name
        self.testing_guild_id = testing_guild_id
        self.initial_extensions = initial_extensions

    async def setup_hook(self) -> None:
        for extension in self.initial_extensions:
            await self.load_extension(extension)

        if self.testing_guild_id:
            guild = discord.Object(self.testing_guild_id)
            # We'll copy in the global commands to test with:
            self.tree.copy_global_to(guild=guild)
            # followed by syncing to the testing guild.
            await self.tree.sync(guild=guild)

        get_db_from_s3(self.db_name)


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

    # Default initialized extensions
    exts = ["lib.cogs.music_cog", "lib.cogs.poll_cog", "lib.cogs.backup_db_cog"]

    async with AndyBot(
        intents=intents,
        command_prefix=commands.when_mentioned_or("!"),
        description="A bot representing NYS's late Governor Andy Cuomo",
        initial_extensions=exts,
    ) as bot:
        await bot.start(os.getenv("DISCORD_TOKEN", ""))


asyncio.run(main())
