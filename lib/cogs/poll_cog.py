from discord.ext import commands

from lib.model.poll import Poll


class PollCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="poll")
    async def poll(self, ctx, poll_name: str):
        member = ctx.author
        poll = Poll(created_by=member.id, poll_name=poll_name)
        poll.record_poll_in_db()


async def setup(bot):
    await bot.add_cog(PollCog(bot))
