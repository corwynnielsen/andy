from datetime import UTC, datetime
from zoneinfo import ZoneInfo


class Vote:
    def __init__(
        self,
        created_by: str,
        display_name: str,
        selectedOption: str | bool,
    ):
        self.created_date = (
            datetime.now(ZoneInfo("America/Denver"))
            .astimezone(UTC)
            .strftime("%Y-%m-%dT%H:%M:%S%z")
        )
        self.created_by = created_by
        self.display_name = display_name
        self.selectedOption = selectedOption
