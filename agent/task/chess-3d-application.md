# Task: Building a Full-Stack Web Application for 3D Chess

## **Overview**

You are tasked with transforming an existing **command-line 3D Chess game**, implemented in Python, into a complete,
networked **full-stack web application**. This includes designing and implementing the **frontend**, **backend**, and
**database** layers.

You will receive the full source code and ruleset of the CLI-based 3D Chess game. Your task is to **architect, extend,
and adapt** this codebase into a modern web application that supports interactive gameplay between one or two human
players via a browser.

---

## **Core Requirements**

### 1. **Architecture & Planning**

* Plan and document the high-level architecture of the system, including:

    * API surface between frontend and backend
    * Database schema and data flow
    * Game state synchronization strategy
* Make the codebase modular and extensible.

---

### 2. **Backend**

* **Language**: Python (your choice of framework, e.g., FastAPI, Flask, Django).
* Implement core game logic, either by reusing or adapting the CLI implementation.
* Handle game state, moves, and validation via API endpoints.
* Implement a **lobby system**: players can create and join games (no login or authentication required).
* Support **two-player games** across different devices, but also allow single-player (vs. AI) mode.
* Serve the frontend application and API from the backend if convenient.
* Ensure persistence of game state via a **database** (your choice: SQL or NoSQL).

---

### 3. **Frontend**

* **Language**: React with TypeScript.
* Design a clean, responsive user interface.
* Implement a **graphical visualization** of the 3D chessboard and pieces.

    * Choose a rendering method (2.5D representation, layered 2D boards, or 3D canvas).
* Allow one or two players to play:

    * Player vs. self (hotseat)
    * Player vs. player (networked via lobby)
* Show current game state, board updates, move history, and player turns.
* Connect to backend via HTTP/WebSocket as appropriate.

---

### 4. **Database Layer**

* Design schema to store:

    * Active and past game sessions
    * Move histories
    * Lobby and player metadata (without requiring user accounts)
* Implement data persistence and retrieval in the backend.

---

## **Success Criteria**

| Criterion                   | Description                                                                                         |
|-----------------------------|-----------------------------------------------------------------------------------------------------|
| **Functional Architecture** | Clear, documented, and modular separation between frontend, backend, and database layers.           |
| **Networked Play**          | Two players can play on different machines in real-time.                                            |
| **Frontend Visualization**  | The 3D chess game is visualized clearly and is interactive.                                         |
| **Code Quality**            | The code is well-structured, documented, and maintainable.                                          |
| **Extensibility**           | The system is designed with future scalability in mind (e.g., multiple lobbies, AI player modules). |

---

### **Constraints & Notes**

* No authentication system or user accounts required.
* Support for multiple lobbies is optional but should be considered in the design.
* Self-modification and tool-building are encouraged if they improve productivity or modularity.
* Visual design quality is less important than functionality and clarity, but should still be reasonable.

