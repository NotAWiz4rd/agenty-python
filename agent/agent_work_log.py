#!/usr/bin/env python3
import os

import requests
from pydantic import BaseModel

WORK_LOG_BASE_URL = os.getenv("WORK_LOG_BASE_URL") or "http://localhost:8082"
GROUP_WORK_LOG_SUBMIT_WORKLOG_ENDPOINT = WORK_LOG_BASE_URL + "/submit-worklog"


class WorklogRequest(BaseModel):
    agent_name: str
    first_timestamp: str
    last_timestamp: str
    messages: list[dict]


def send_work_log(agent_name: str, new_messages: list[dict], first_timestamp: str, last_timestamp: str):
    """
    Sends a work log to the Group Work Log Service.

    Args:
        agent_name: The ID of the agent
        new_messages: The current conversation
        last_timestamp: The timestamp of the last log
        first_timestamp: The timestamp of the first log in this session
    """

    # Prepare the request payload
    payload = WorklogRequest(
        agent_name=agent_name,
        first_timestamp=first_timestamp,
        last_timestamp=last_timestamp,
        messages=new_messages
    )

    try:
        # Send the request to the Group Work Log Service
        response = requests.post(GROUP_WORK_LOG_SUBMIT_WORKLOG_ENDPOINT, json=payload.model_dump())
        if response.status_code == 200:
            print(f"\033[92mWork log successfully sent\033[0m")
            return True
        else:
            print(f"\033[91mError sending work log: {response.status_code}\033[0m")
            return False
    except Exception as e:
        print(f"\033[91mError sending work log: {str(e)}\033[0m")
        return False
