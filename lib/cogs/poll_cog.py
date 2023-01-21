import asyncio
from typing import Optional
from discord.ext import commands

from lib.util.state import State
from lib.model.poll import Poll
from lib.service import poll_service

POLL_TIME_MULTIPLIER = 5


class PollCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.current_poll: Optional[Poll] = None

    @commands.group(name="poll", invoke_without_command=True)
    async def poll(self, ctx: commands.Context, name: str):
        # No current poll exists, create and record in DB
        if self.current_poll is None:
            member = ctx.author
            self.current_poll = Poll(created_by=member.id, name=name)
            await self.current_poll.record_poll(self.current_poll)
            await ctx.send("Poll '{}' created successfully".format(name))
            return

        # When current_poll not none, there is an existing poll either in DRAFT or IN_PROGRESS state
        await ctx.send("There can only be one poll at a time")
        return

    @poll.command(name="confirm")
    async def confirm_poll_and_send_results(self, ctx: commands.Context):
        if self.current_poll is not None:
            name = self.current_poll.name

            # When poll is confirmed in draft state, mark as in progress and start poll timer
            if self.current_poll.state == State.DRAFT:
                await self.current_poll.mark_in_progress()
                await ctx.send(
                    "Poll '{}' is in progress and you may start voting now".format(name)
                )

                # Wait for poll to complete in specified time before sending results
                await asyncio.sleep(
                    float(self.current_poll.time_limit * POLL_TIME_MULTIPLIER)
                )

                # Send results as embed, mark current_poll as done, and reset_current poll to None
                await ctx.send(embed=self.current_poll.results())
                await self.current_poll.mark_done()
                self.current_poll = None
                return

            # Poll must already be in progress if not in draft state
            await ctx.send("Poll '{}' is already in progress".format(name))
            return

        # Poll is none so here is current
        await ctx.send("There isn't a poll to confirm")
        return

    @poll.command(name="vote", aliases=["v"])
    async def vote(self, ctx: commands.Context, selected_option: int):
        # Check if there is a poll in progress
        if (
            self.current_poll is not None
            and self.current_poll.state == State.IN_PROGRESS
        ):
            # Attempt to place vote for calling member
            member = ctx.author
            option_name = self.current_poll.options.get(selected_option, None)
            vote_success = await self.current_poll.record_vote(
                is_bot_owner=await self.bot.is_owner(member),
                created_by=member.id,
                display_name=member.display_name,
                selected_option={
                    "id": selected_option,
                    "option_name": option_name,
                },
            )

            # Vote was placed successfully
            if vote_success:
                await ctx.send(
                    "{} Vote for option '{}' successful!".format(
                        member.mention, option_name
                    )
                )
                return

            # Vote failed to be placed due to invalid vote option or uplicate vote entry
            await ctx.send(
                "{} You've selected an invalid vote value or you've already placed a vote for this poll".format(
                    member.mention
                )
            )
            return

        # No in progress Poll found to vote on
        await ctx.send("There isn't a poll in progress yet")
        return

    @poll.command(name="cancel")
    async def cancel(self, ctx: commands.Context):
        member = ctx.author
        if self.current_poll is not None and self.current_poll.state == State.DRAFT:
            owner = await self.bot.fetch_user(self.current_poll.created_by)
            if member.id == owner.id:
                await self.current_poll.mark_cancelled()
                await ctx.send(
                    "Poll '{}' successfully cancelled".format(self.current_poll.name)
                )
                self.current_poll = None
                return

            await ctx.send(
                "Polls can only be cancelled by the poll owner {}".format(owner.mention)
            )
            return

        await ctx.send(
            "Poll is currently in progress and cannot be cancelled or there is no current poll to cancel"
        )
        return

    @poll.command(name="results")
    async def results(self, ctx: commands.Context):
        latest = await poll_service.get_latest()
        if latest:
            await ctx.send(embed=latest.results())
            return

        await ctx.send("There are no polls to get results from")
        return


async def setup(bot):
    await bot.add_cog(PollCog(bot))
