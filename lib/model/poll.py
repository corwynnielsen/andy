from typing import Dict, List, Optional, Self
from datetime import UTC, datetime
from zoneinfo import ZoneInfo
from discord import Embed

from lib.data import poll_data_service
from lib.model.vote import Vote
from lib.util.state import State


class Poll:
    def __init__(
        self,
        created_by: int,
        name: str,
        time_limit: int = 3,
        options: Optional[Dict[int, str]] = None,
        state: State = State.DRAFT,
        votes: Optional[List[Vote]] = None,
        created_date: Optional[str] = None,
    ):
        self.created_by = created_by
        self.name = name
        self.time_limit = time_limit
        self.options = options if options else {1: "Yes", 2: "No"}
        self.state = state
        self.votes = votes if votes else []
        self.created_date = (
            created_date
            if created_date
            else (
                datetime.now(ZoneInfo("America/Denver"))
                .astimezone(UTC)
                .strftime("%Y-%m-%dT%H:%M:%S%z")
            )
        )

    async def record_poll(self, poll: Self) -> int:
        return await poll_data_service.record_poll(poll)

    async def record_vote(
        self,
        is_bot_owner: bool,
        created_by: int,
        display_name: str,
        selected_option: dict,
    ) -> bool:
        if not is_bot_owner:
            user_has_existing_vote = await poll_data_service.get_vote_for_user(
                created_by, [State.IN_PROGRESS]
            )
            if user_has_existing_vote:
                return False

        # Check to disallow invalid voting options. Invalid options are passed in with option_name None
        if not selected_option["option_name"]:
            return False

        vote = Vote(
            created_by=created_by,
            display_name=display_name,
            selected_option=selected_option,
        )
        self.votes.append(vote)
        await poll_data_service.record_vote(self.votes)

        return True

    async def mark_in_progress(self) -> Self:
        await poll_data_service.update_poll_state(State.IN_PROGRESS)
        self.state = State.IN_PROGRESS
        return self

    async def mark_done(self) -> Self:
        await poll_data_service.update_poll_state(State.DONE)
        self.state = State.DONE
        return self

    async def mark_cancelled(self) -> Self:
        await poll_data_service.update_poll_state(State.CANCELLED)
        self.state = State.CANCELLED
        return self

    def results(self) -> Embed:
        tallied_votes = {
            int(item[0]): {"vote_count": 0, "option_name": item[1]}
            for item in self.options.items()
        }
        for vote in self.votes:
            #  Tally vote count
            tallied_votes[vote.selected_option["id"]]["vote_count"] += 1

        # Sort above dict items by option ID so it's in the correct order for embed display
        sorted_by_id_vote_tallies = [
            vote[1] for vote in sorted(tallied_votes.items(), key=lambda item: item[0])
        ]

        # Populate embed with fields based on tallies
        embed = Embed(title=self.name)
        for vote_tally in sorted_by_id_vote_tallies:
            embed.add_field(
                name=vote_tally["option_name"],
                value=vote_tally["vote_count"],
                inline=True,
            )

        # Get winners by max total vote count and add winner to footer of embed
        highest_votes = max(
            sorted_by_id_vote_tallies, key=lambda item: item["vote_count"]
        )
        vote_winners = [
            vote_tally
            for vote_tally in sorted_by_id_vote_tallies
            if vote_tally["vote_count"] == highest_votes["vote_count"]
        ]

        if len(vote_winners) > 1:
            embed.set_footer(text="Winner: {}-way tie".format(len(vote_winners)))
        else:
            embed.set_footer(
                text="Winner: {}".format(vote_winners.pop()["option_name"])
            )

        return embed
