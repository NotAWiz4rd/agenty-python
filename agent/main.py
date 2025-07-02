# Register cleanup function to run on exit
import atexit
import sys

import anthropic

from api import start_api
from base_agent import Agent
from context_handling import (cleanup_context)
from team_config_loader import get_team_config, get_current_agent_name
from util import log_error, get_agent_turn_delay_in_ms


def main():
    anthropic_client = anthropic.Anthropic()  # expects ANTHROPIC_API_KEY in env

    team_config = get_team_config()
    # Set team mode to True only if multiple agents are defined in the configuration
    team_mode = False if not team_config or len(team_config.agents) <= 1 else True
    number_of_agents = len(team_config.agents) if team_mode else 1

    atexit.register(cleanup_context)

    try:
        start_api(team_config.get_current_agent())
        agent_name = get_current_agent_name()

        agent = Agent(agent_name, anthropic_client, team_mode, turn_delay=get_agent_turn_delay_in_ms(number_of_agents))
        print(f"\033[92mStarting Agent named {agent_name}.\033[0m")
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
