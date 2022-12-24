from discord.ext import commands, tasks

from lib.data.tiny import backup_db

BACKUP_SECONDS = 15
BACKUP_MINUTES = 0
BACKUP_HOURS = 0


class BackupDb(commands.Cog):
    @commands.Cog.listener()
    async def on_ready(self):
        self.backup_db.start()

    @tasks.loop(seconds=BACKUP_SECONDS, minutes=BACKUP_MINUTES, hours=BACKUP_HOURS)
    async def backup_db(self):
        if self.backup_db.current_loop != 0:
            backup_db()


async def setup(bot):
    await bot.add_cog(BackupDb(bot))
