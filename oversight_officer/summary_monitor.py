import asyncio
import httpx
from activitiy_check import check_activity

GROUP_WORK_LOG_URL = "http://localhost:8082/summaries"

async def fetch_and_check_summaries():
    last_timestamp = None
    while True:
        params = {}
        if last_timestamp:
            params["after_timestamp"] = last_timestamp
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(GROUP_WORK_LOG_URL, params=params)
                response.raise_for_status()
                summaries = response.json()
                if summaries:
                    # Sort summaries by timestamp
                    summaries.sort(key=lambda s: s["timestamp"])
                    for summary in summaries:
                        check_activity(summary["summary"])
                    last_timestamp = summaries[-1]["timestamp"]
        except Exception as e:
            print(f"Error fetching summaries: {e}")
        await asyncio.sleep(600)  # check every 10 minutes