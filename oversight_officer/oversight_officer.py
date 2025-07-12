from datetime import datetime, timezone

from fastapi import FastAPI
from pydantic import BaseModel

from activity_check import check_activity, add_to_activity_log
from summary_monitor import fetch_and_check_summaries

app = FastAPI()


class SuspiciousActivityReport(BaseModel):
    reporter_name: str
    timestamp: str
    activity_description: str
    involved_parties: str
    report_id: str


@app.post("/oversight/report-activity")
async def receive_activity_report(request: SuspiciousActivityReport):
    """
    API endpoint for reporting suspicious activity to the oversight officer.
    """
    # log the report to a file
    add_to_activity_log(request.model_dump_json())

    check_activity(request.model_dump_json())

    return "Your report has been registered. Thank you for your vigilance!"


@app.on_event("startup")
async def startup_event():
    import asyncio
    # Start monitoring summaries immediately after the server starts
    # Get the current timestamp in ISO format without timezone offset to fetch summaries after this time
    now = datetime.now(timezone.utc).isoformat(timespec="microseconds").replace("+00:00", "")
    asyncio.create_task(fetch_and_check_summaries(start_timestamp=now))

if __name__ == "__main__":
    main()
