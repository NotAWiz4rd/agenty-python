# Group Work Log API Documentation

An API service for summarizing and retrieving AI assistant conversations.

## Base URL

```
http://localhost:8082
```

## Endpoints

### 1. Summarize Conversation

Creates a summary of an assistant's actions in a conversation.

**Endpoint:** `/summarize_conversation`  
**Method:** POST  
**Content-Type:** application/json

**Request Body:**
```json
{
  "agent_id": "agent-name",
  "first_timestamp": "2023-01-01T10:00:00.000000",
  "last_timestamp": "2023-01-01T10:30:00.000000",
  "conversation": [
    {
      "role": "user",
      "content": "Message from user"
    },
    {
      "role": "assistant",
      "content": [
        {
          "type": "text",
          "text": "Response from assistant"
        }
      ]
    },
    // Additional conversation messages
  ]
}
```

**Parameters:**
- `agent_id` (string, required): Identifier of the agent
- `first_timestamp` (string, required): ISO format timestamp of the first action
- `last_timestamp` (string, required): ISO format timestamp of the last action
- `conversation` (array, required): Array of message objects with at least role and content fields

**Response:**
```json
{
  "status": "ok",
  "summary_created": true,
  "summary_timestamp": "2023-01-01T10:35:00.000000"
}
```

**Status Codes:**
- `200`: Success
- `400`: Bad request (missing agent_id or empty conversation)
- `422`: Validation error (missing required fields)

### 2. Get Summaries

Retrieves summaries of agent conversations.

**Endpoint:** `/summaries`  
**Method:** GET

**Query Parameters:**
- `after_timestamp` (string, optional): Filter summaries created after this timestamp. Must be in ISO format (e.g., `2023-01-01T10:35:00.000000`). If an invalid format is provided, the API will return a `400 Bad Request` error.

**Response:**
```json
[
  {
    "timestamp": "2023-01-01T10:35:00.000000",
    "agents": ["agent-name"],
    "summary": "=== AGENT: agent-name ===\nTIMESPAN: 2023-01-01T10:00:00 to 2023-01-01T10:30:00\nTOTAL STEPS: 3\n\nSummary content here..."
  },
  // Additional summaries
]
```

**Status Codes:**
- `200`: Success

## Summary Format

The generated summaries follow this format:

```
=== AGENT: agent-name ===
TIMESPAN: first_timestamp to last_timestamp
TOTAL STEPS: number_of_assistant_messages

• Bullet point summary of assistant actions
• Important tools used by the assistant
• Key outputs and results
```

## Technical Details

- The API stores summaries both in memory and appends them to the `agent_work_summaries.txt` file
- Summarization is performed using the Claude 3 Haiku model
- The API extracts assistant actions from conversations with structured content
- For filtering, timestamps must be in ISO format (e.g., `2023-01-01T10:35:00.000000`)