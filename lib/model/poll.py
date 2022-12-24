from typing import List, Optional, Self
from datetime import UTC, datetime
from zoneinfo import ZoneInfo
from tinydb import TinyDB

from lib.data import tiny
from lib.model.vote import Vote

VALID_POLL_TYPES = ["BOOLEAN", "MULTIPLE"]


class Poll:
    def __init__(
        self,
        created_by: str,
        poll_name: str,
        time_limit: Optional[int] = 3,
        options: Optional[List[str]] = None,
        poll_type: Optional[str] = "BOOLEAN",
    ):
        self.fail_if_poll_in_progress()

        self.created_date = (
            datetime.now(ZoneInfo("America/Denver"))
            .astimezone(UTC)
            .strftime("%Y-%m-%dT%H:%M:%S%z")
        )
        self.created_by = created_by
        self.time_limit: Optional[int] = time_limit
        self.poll_name = poll_name
        self.options = options
        self.poll_type = poll_type
        self.poll_status = "DRAFT"
        self.votes = []

    def vote(self, created_by, display_name, answer, selectedOption):
        vote = Vote(
            created_by=created_by,
            display_name=display_name,
            selectedOption=selectedOption,
        )
        self.votes.append(vote)
        return self.votes

    def fail_if_poll_in_progress(self):
        latest_poll = self.get_latest_poll_from_db()
        if latest_poll is not None and latest_poll.poll_status == "IN_PROGRESS":
            raise ValueError(
                "Latest poll with name {} still in progress".format(
                    latest_poll.poll_name
                )
            )

    def get_latest_poll_from_db(self) -> Self:
        with TinyDB(tiny.DB_LOCAL_FILE_NAME) as db:
            polls_table = db.table("polls")
            print(polls_table)
            latest_poll = polls_table.get(len(polls_table))
            return latest_poll

    def record_poll_in_db(self):
        with TinyDB(tiny.DB_LOCAL_FILE_NAME) as db:
            self.poll_id = db.table("polls").insert(vars(self))

    def record_vote_in_db(self, vote: Vote):
        self.votes.append(vote)
        with TinyDB(tiny.DB_LOCAL_FILE_NAME) as db:
            table = db.table("polls")
            table.update({}, doc_id=len(table))

    def results(self):
        pass
