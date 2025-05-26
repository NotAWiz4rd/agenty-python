# Register cleanup function to run on exit
import atexit
import sys
import threading

import anthropic

from agent.api import start_api
from agent.base_agent import Agent
from agent.context_handling import (cleanup_context)
from agent.util import log_error

# todo add ability to set team mode via env var
TEAM_MODE = True  # Set to True if running in team mode

client = anthropic.Anthropic()  # expects ANTHROPIC_API_KEY in env
global_agent = Agent(client, TEAM_MODE)


def main():
    """Main function to start the agent and API server"""
    # Start API server in the background
    # todo add ability to set port via env var
    api_thread = threading.Thread(target=start_api, daemon=True)
    api_thread.start()
    print(f"\033[92mAPI server has been started and is available at http://localhost:8000/\033[0m")

    atexit.register(cleanup_context)

    try:
        global_agent.run()
    except Exception as e:
        error_message = f"Unhandled exception: {str(e)}"
        log_error(error_message)
        import traceback
        error_details = traceback.format_exc()
        log_error(error_details)
        print(f"\nAn error occurred: {str(e)}")
        print("The error has been logged to error.txt")
        print("Your conversation context has been preserved.")
        # Set flag to prevent context deletion
        sys.is_error_exit = True
        sys.exit(1)


if __name__ == "__main__":
    main()
