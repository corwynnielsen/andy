from datetime import UTC, datetime
from typing import Dict, Optional
from zoneinfo import ZoneInfo
import json
from tinydb_serialization import SerializationMiddleware, Serializer
from aiotinydb.middleware import AIOMiddlewareMixin
from aiotinydb.storage import AIOJSONStorage


class Vote:
    def __init__(
        self,
        created_by: int,
        display_name: str,
        selected_option: Dict,
        created_date: Optional[str] = None,
    ):
        self.created_by = created_by
        self.display_name = display_name
        self.selected_option = selected_option
        self.created_date = (
            created_date
            if created_date
            else (
                datetime.now(ZoneInfo("America/Denver"))
                .astimezone(UTC)
                .strftime("%Y-%m-%dT%H:%M:%S%z")
            )
        )

        if "id" in self.selected_option:
            self.selected_option["id"] = int(self.selected_option["id"])


class VoteSerializerMiddleware(Serializer):
    OBJ_CLASS = Vote  # type: ignore

    def encode(self, obj):
        return json.dumps(vars(obj))

    def decode(self, s):
        json_as_obj = json.loads(s)
        return Vote(**json_as_obj)


class AIOAwareVoteSerializerMiddleware(VoteSerializerMiddleware, AIOMiddlewareMixin):
    pass


vote_serializer = SerializationMiddleware(AIOJSONStorage)
vote_serializer.register_serializer(
    AIOAwareVoteSerializerMiddleware(AIOJSONStorage), "VoteSerializer"
)
