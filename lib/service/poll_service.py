from typing import Optional, Self

from lib.model.poll import Poll
from lib.data.poll_data_service import get_latest_poll


async def get_latest() -> Optional[Poll]:
    latest = await get_latest_poll()
    if latest is not None:
        return Poll(**latest)
