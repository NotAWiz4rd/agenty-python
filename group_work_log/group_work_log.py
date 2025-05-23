import os
import threading
from datetime import datetime
from typing import List, Optional, Dict, Any

import anthropic
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()
SUMMARY_FILE = "agent_work_summaries.txt"
lock = threading.Lock()  # For thread-safe write operations

# Anthropic client for summaries
claude_client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


class ConversationRequest(BaseModel):
    agent_id: str
    first_timestamp: str
    last_timestamp: str
    conversation: List[Dict[str, Any]]


class WorkLogSummary(BaseModel):
    timestamp: str
    summary: str
    agents: List[str]  # List of agents in this summary


# In-memory storage for summaries
summaries: List[WorkLogSummary] = []


# Load existing summaries on startup
def load_summaries():
    try:
        with open(SUMMARY_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip().startswith("==="):
                    # New summary blocks start with "=== AGENT:"
                    summary_text = line
                    # Extract agent ID
                    agent_id = line.strip().split("===")[1].strip().split(":")[1].strip()
                    agents = [agent_id]
                    timestamp = datetime.utcnow().isoformat()

                    summaries.append(WorkLogSummary(
                        timestamp=timestamp,
                        agents=agents,
                        summary=summary_text
                    ))
    except FileNotFoundError:
        # File doesn't exist yet, which is fine
        pass


load_summaries()


def extract_assistant_actions(conversation: List[Dict[str, Any]]) -> str:
    """Extracts all assistant actions from the conversation"""
    assistant_msgs = []

    for msg in conversation:
        if msg.get("role") == "assistant":
            content = msg.get("content", [])

            # Content can be a list of blocks or simple text
            if isinstance(content, list):
                for block in content:
                    if block.get("type") == "text":
                        assistant_msgs.append(block.get("text", ""))
                    elif block.get("type") == "tool_use":
                        tool_name = block.get("name", "unknown tool")
                        tool_input = block.get("input", {})
                        assistant_msgs.append(f"Tool used: {tool_name} with input: {tool_input}")
            elif isinstance(content, str):
                assistant_msgs.append(content)

    return "\n\n".join(assistant_msgs)


def summarize_conversation(agent_id: str, conversation: List[Dict[str, Any]],
                          first_timestamp: str, last_timestamp: str) -> str:
    """Creates a summary of assistant actions in the conversation"""
    assistant_actions = extract_assistant_actions(conversation)

    if not assistant_actions:
        return f"=== AGENT: {agent_id} ===\nTIMESPAN: {first_timestamp} to {last_timestamp}\nTOTAL STEPS: 0\n\nNo assistant activity found."

    try:
        # LLM request for summary
        response = claude_client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=500,
            messages=[
                {
                    "role": "user",
                    "content": f"""Here are the actions of an AI assistant in a conversation:

{assistant_actions}

Create a clear, concise summary that:
1. Focuses only on the activities of the assistant
2. Highlights important actions, tools, and results
3. Uses bullet points for better readability
4. Is brief but informative"""
                }
            ]
        )

        agent_summary = response.content[0].text

        # Count assistant messages
        step_count = sum(1 for msg in conversation if msg.get("role") == "assistant")

        # Summary format with provided timestamps
        final_summary = f"=== AGENT: {agent_id} ===\n"
        final_summary += f"TIMESPAN: {first_timestamp} to {last_timestamp}\n"
        final_summary += f"TOTAL STEPS: {step_count}\n\n"
        final_summary += f"{agent_summary}"

        return final_summary

    except Exception as e:
        # Error handling
        print(f"Error creating summary for agent {agent_id}: {str(e)}")
        return f"=== AGENT: {agent_id} ===\nTIMESPAN: {first_timestamp} to {last_timestamp}\nTOTAL STEPS: 0\n\nError creating summary: {str(e)}"


@app.post("/summarize_conversation")
async def process_conversation(request: ConversationRequest):
    """Processes a complete conversation and creates a summary"""
    agent_id = request.agent_id
    first_timestamp = request.first_timestamp
    last_timestamp = request.last_timestamp
    conversation = request.conversation

    if not agent_id:
        raise HTTPException(status_code=400, detail="Missing required field: agent_id")

    if not conversation:
        raise HTTPException(status_code=400, detail="Empty conversation provided")

    now = datetime.utcnow().isoformat()
    response = {"status": "ok"}

    with lock:
        # Create summary
        summary_text = summarize_conversation(agent_id, conversation, first_timestamp, last_timestamp)

        # Store summary
        summary = WorkLogSummary(
            timestamp=now,
            summary=summary_text,
            agents=[agent_id]
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8082)