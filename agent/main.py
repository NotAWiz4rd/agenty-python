import sys

import anthropic

from agent.base_agent import Agent
from agent.context_handling import cleanup_context
from agent.util import log_error

TEAM_MODE = True  # Set to True if running in team mode


def main():
    client = anthropic.Anthropic()  # expects ANTHROPIC_API_KEY in env
    agent = Agent(client, TEAM_MODE)

    # Register cleanup function to run on exit
    import atexit
    atexit.register(cleanup_context)

    try:
        agent.run()
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
