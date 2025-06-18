# Register cleanup function to run on exit
import atexit
import sys

import anthropic

from agent.api import start_api
from agent.base_agent import Agent
from agent.context_handling import (cleanup_context)
from agent.team_config_loader import get_team_config
from agent.util import log_error


def main():
    anthropic_client = anthropic.Anthropic()  # expects ANTHROPIC_API_KEY in env

    team_config = get_team_config()
    # Set team mode to True only if multiple agents are defined in the configuration
    team_mode = False if not team_config or len(team_config.agents) <= 1 else True

    start_api(team_config.get_current_agent())

    atexit.register(cleanup_context)

    try:
        agent = Agent(anthropic_client, team_mode, team_config)
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
