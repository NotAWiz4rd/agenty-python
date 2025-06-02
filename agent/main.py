# Register cleanup function to run on exit
import atexit
import sys

import anthropic

from agent.api import start_api
from agent.base_agent import Agent
from agent.context_handling import (cleanup_context)
from agent.team_config_loader import load_team_config
from agent.util import log_error


# Load team configuration
TEAM_CONFIG = load_team_config()
# Set team mode to True only if multiple agents are defined in the configuration
TEAM_MODE = len(TEAM_CONFIG.agents) > 1

client = anthropic.Anthropic()  # expects ANTHROPIC_API_KEY in env
global_agent = Agent(client, TEAM_MODE, TEAM_CONFIG)


def main():
    if TEAM_MODE:
        start_api(TEAM_CONFIG.current_agent)

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
