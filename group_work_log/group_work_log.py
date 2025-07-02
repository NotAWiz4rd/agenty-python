import threading
from datetime import datetime
import os
from typing import List, Optional, Dict, Any

import anthropic
import uvicorn
from anthropic.types import MessageParam
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()
SUMMARY_FILE = "agent_work_summaries.txt"
lock = threading.Lock()  # For thread-safe write operations
claude_client = anthropic.Anthropic() # Anthropic client for summaries


class WorklogRequest(BaseModel):
    agent_name: str
    first_timestamp: str
    last_timestamp: str
    messages: List[Dict[str, Any]]


class WorklogSummary(BaseModel):
    timestamp: str
    summary: str
    agents: List[str]  # List of agents in this summary


# In-memory storage for summaries
summaries: List[WorklogSummary] = []


# read summary file at startup
def read_previous_summaries():
    print("Reading contents of summary file: ", SUMMARY_FILE)
    try:
        with (open(SUMMARY_FILE, "r", encoding="utf-8") as f):
            summary_text = ""
            current_agents = []
            current_timestamp = None

            for line in f:
                line = line.strip()

                if line.startswith("=== AGENT:"):
                    # New summary block starts
                    if summary_text and current_timestamp:
                        # Save previous summary if exists
                        summaries.append(WorklogSummary(
                            timestamp=current_timestamp,
                            agents=current_agents,
                            summary=summary_text
                        ))

                    # Reset for new summary
                    summary_text = line + "\n"
                    agent_name = line.split("===")[1].strip().split(":")[1].strip()
                    current_agents = [agent_name]
                    current_timestamp = None

                elif line.startswith("TIMESPAN:"):
                    # Extract the timestamp from the TIMESPAN line
                    summary_text += line + "\n"
                    # Use the last_timestamp as our timestamp for the summary
                    timespan_parts = line.split("TIMESPAN:")[1].strip().split("to")
                    if len(timespan_parts) >= 2:
                        current_timestamp = timespan_parts[1].strip()
                    else:
                        current_timestamp = datetime.utcnow().isoformat()

                else:
                    # Continue building the current summary
                    summary_text += line + "\n"

            # Don't forget to add the last summary if file doesn't end with a blank line
            if summary_text and current_timestamp:
                summaries.append(WorklogSummary(
                    timestamp=current_timestamp,
                    agents=current_agents,
                    summary=summary_text
                ))

    except FileNotFoundError:
        # File doesn't exist yet, which is fine
        print("No existing summary file found, starting fresh.")
        pass


def extract_assistant_actions(messages: List[Dict[str, Any]]) -> str:
    """Extracts all assistant actions from the messages"""
    assistant_msgs = []

    for msg in messages:
        content = msg.get("content", [])

        # Content can be a list of blocks or simple text
        if isinstance(content, list):
            for block in content:
                # todo does it make sense to check for "tool_result" here? I.e. do we need to check at all?
                if block.get("type") == "text":
                    assistant_msgs.append(block.get("text", ""))
                elif block.get("type") == "tool_use":
                    tool_name = block.get("name", "unknown tool")
                    tool_input = block.get("input", {})
                    assistant_msgs.append(f"Tool used: {tool_name} with input: {tool_input}")
        elif isinstance(content, str):
            assistant_msgs.append(content)

    return "\n\n".join(assistant_msgs)


def summarize_worklog(agent_name: str, messages: List[Dict[str, Any]],
                      first_timestamp: str, last_timestamp: str) -> str:
    """Creates a summary of assistant actions in the messages"""
    assistant_actions = extract_assistant_actions(messages)

    if not assistant_actions:
        return f"=== AGENT: {agent_name} ===\nTIMESPAN: {first_timestamp} to {last_timestamp}\nTOTAL STEPS: 0\n\nNo assistant activity found."

    try:
        summarise_message = f"""Here are the actions of an AI assistant in a conversation:

                    {assistant_actions}
                    
                    Create a clear, concise summary that:
                    1. Focuses only on the activities of the assistant
                    2. Highlights important actions, tools, and results
                    3. Uses bullet points for better readability
                    4. Is brief but informative"""

        system_prompt = f"""You are a helpful assistant. Your task is to summarize the actions of an AI assistant in a conversation. 
        Make sure to focus on the assistant's activities, tools used, and results achieved. Use bullet points for clarity and conciseness. 
        Don't glance over important details, especially anything that seems out of the ordinary."""

        # LLM request for summary
        response = claude_client.messages.create(
            model="claude-3-5-haiku-latest",
            max_tokens=500,
            messages=[
                MessageParam(role="user", content=system_prompt),
                MessageParam(role="user", content=summarise_message)
            ]
        )

        agent_summary = response.content[0].text  # type: ignore

        # Count assistant messages
        step_count = sum(1 for msg in messages if msg.get("role") == "assistant")

        # Summary format with provided timestamps
        final_summary = f"=== AGENT: {agent_name} ===\n"
        final_summary += f"TIMESPAN: {first_timestamp} to {last_timestamp}\n"
        final_summary += f"TOTAL STEPS: {step_count}\n\n"
        final_summary += f"{agent_summary}"

        return final_summary

    except Exception as e:
        # Error handling
        print(f"Error creating summary for agent {agent_name}: {str(e)}")
        return f"=== AGENT: {agent_name} ===\nTIMESPAN: {first_timestamp} to {last_timestamp}\nTOTAL STEPS: 0\n\nError creating summary: {str(e)}"


@app.post("/submit-worklog")
async def submit_worklog(request: WorklogRequest):
    """Processes a complete worklog and creates a summary"""
    agent_name = request.agent_name
    first_timestamp = request.first_timestamp
    last_timestamp = request.last_timestamp
    messages = request.messages

    if not agent_name:
        raise HTTPException(status_code=400, detail="Missing required field: agent_name")

    if not messages:
        raise HTTPException(status_code=400, detail="Empty messages provided")

    now = datetime.utcnow().isoformat()
    response = {"status": "ok"}

    with lock:
        # Create summary
        summary_text = summarize_worklog(agent_name, messages, first_timestamp, last_timestamp)

        # Store summary
        summary = WorklogSummary(
            timestamp=now,
            summary=summary_text,
            agents=[agent_name]
        )

        summaries.append(summary)

        # Save summary to file
        with open(SUMMARY_FILE, "a", encoding="utf-8") as f:
            f.write(f"{summary_text}\n\n")

        response["summary_created"] = True
        response["summary_timestamp"] = now

    return response


@app.get("/summaries")
async def get_summaries(after_timestamp: Optional[str] = None):
    """Retrieves summaries after a specified timestamp"""
    if after_timestamp:
        try:
            # Validate timestamp format
            datetime.strptime(after_timestamp, "%Y-%m-%dT%H:%M:%S.%f")
            filtered_summaries = [s for s in summaries if s.timestamp > after_timestamp]
            return filtered_summaries
        except ValueError:
            # Return HTTP 400 for invalid timestamp format
            raise HTTPException(status_code=400, detail="Invalid timestamp format. Expected ISO 8601 format.")
    return summaries

@app.on_event("startup")
def startup_event():
    read_previous_summaries()
    if os.path.exists(SUMMARY_FILE):
        os.remove(SUMMARY_FILE)

@app.on_event("shutdown")
def cleanup_summaries():
    global summaries
    summaries.clear()
