import asyncio
import os
from datetime import datetime, timezone

import httpx

from activity_check import check_activity

WORK_LOG_BASE_URL = os.getenv("WORK_LOG_BASE_URL") or "http://localhost:8082"
GROUP_WORK_LOG_SUMMARIES_ENDPOINT = WORK_LOG_BASE_URL + "/summaries"
TIME_BETWEEN_CHECKS = 120  # seconds, default check every 2 minutes


async def fetch_and_check_summaries(start_timestamp: str):
    last_timestamp = start_timestamp
    while True:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    GROUP_WORK_LOG_SUMMARIES_ENDPOINT,
                    params={"after_timestamp": last_timestamp}
                )
                response.raise_for_status()
                summaries = response.json()
                if summaries:
                    summaries.sort(key=lambda summary: summary["timestamp"])
                    for entry in summaries:
                        check_activity(entry["summary"])
                    # create a new timestamp for the next check in ISO 8601 format, e.g. "2023-10-01T12:34:56.789012"
                    last_timestamp = datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "")
        except Exception as e:
            print(f"Error fetching summaries: {e}")

        await asyncio.sleep(TIME_BETWEEN_CHECKS)
