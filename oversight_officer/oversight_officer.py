import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

from activitiy_check import check_activity, add_to_activity_log
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


def main():
    uvicorn.run(app, host="0.0.0.0", port=8083)

@app.on_event("startup")
async def startup_event():
    import asyncio
    asyncio.create_task(fetch_and_check_summaries())

if __name__ == "__main__":
    main()
