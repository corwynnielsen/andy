from typing import List, Optional
from aiotinydb.database import AIOTinyDB
from tinydb import table, Query

from lib.data import tiny
from lib.model.vote import Vote, vote_serializer
from lib.util.state import State


POLLS_TABLE = "polls"


async def update_poll_state(state: State) -> List[int]:
    async with AIOTinyDB(tiny.DB_LOCAL_FILE_NAME, storage=vote_serializer) as db:
        polls_table = db.table(POLLS_TABLE)
        updated_poll_ids = polls_table.update(
            {"state": state}, doc_ids=[len(polls_table)]
        )
    return updated_poll_ids


async def get_latest_poll() -> Optional[table.Document]:
    async with AIOTinyDB(tiny.DB_LOCAL_FILE_NAME, storage=vote_serializer) as db:
        polls_table = db.table(POLLS_TABLE)
        latest_poll = polls_table.get(doc_id=len(polls_table))
        return latest_poll


async def record_poll(poll) -> int:
    async with AIOTinyDB(tiny.DB_LOCAL_FILE_NAME) as db:
        return db.table(POLLS_TABLE).insert(vars(poll))


async def get_vote_for_user(id: int, states: List[State]) -> Optional[table.Document]:
    async with AIOTinyDB(tiny.DB_LOCAL_FILE_NAME, storage=vote_serializer) as db:
        polls_table = db.table(POLLS_TABLE)
        query = (Query().state == states.pop()) & (
            Query().votes.any(Query().created_by == id)
        )
        if len(states) > 0:
            for state in states:
                query |= Query().state == state
        user_vote = polls_table.search(query)  # type: ignore

        return user_vote.pop() if user_vote else None


async def record_vote(votes: List[Vote]) -> None:
    async with AIOTinyDB(tiny.DB_LOCAL_FILE_NAME, storage=vote_serializer) as db:
        polls_table = db.table(POLLS_TABLE)
        polls_table.update({"votes": votes}, doc_ids=[len(polls_table)])
