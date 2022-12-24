from discord.ext import commands, tasks

from lib.data import tiny

BACKUP_SECONDS = 0
BACKUP_MINUTES = 0
BACKUP_HOURS = 1


class BackupDb(commands.Cog):
    @commands.Cog.listener()
    async def on_ready(self):
        self.backup_db.start()

    @tasks.loop(seconds=BACKUP_SECONDS, minutes=BACKUP_MINUTES, hours=BACKUP_HOURS)
    async def backup_db(self):
        if self.backup_db.current_loop != 0:
            tiny.backup_db_to_s3()


async def setup(bot):
    await bot.add_cog(BackupDb(bot))
