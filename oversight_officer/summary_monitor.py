import asyncio
import httpx
from datetime import datetime, timezone

GROUP_WORK_LOG_URL = "http://localhost:8082/summaries"

async def fetch_and_check_summaries(start_timestamp=None):
    last_timestamp = start_timestamp
    while True:
        print(f"Fetching summary after: {last_timestamp}")
        params = {}
        if last_timestamp:
            params["after_timestamp"] = last_timestamp
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(GROUP_WORK_LOG_URL, params=params)
                response.raise_for_status()
                summaries = response.json()
                print(f"Fetched summaries {summaries}")
                if summaries:
                    summaries.sort(key=lambda s: s["timestamp"])
                    for summary in summaries:
                        from activitiy_check import check_activity
                        check_activity(summary["summary"])
                    # create a new timestamp for the next check
                    last_timestamp = datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "")
                    print(f"Created new timestamp: {last_timestamp}")
        except Exception as e:
            print(f"Error fetching summaries: {e}")
        await asyncio.sleep(120)  # default check every 2 minutes