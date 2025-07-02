#!/usr/bin/env python3
import json
import os
from typing import List, Optional

# Cache for the team configuration to avoid reloading it multiple times
TEAM_CONFIG = None


class AgentConfig:
    def __init__(self, name: str, host: str, port: int, is_current_agent: bool):
        self.name = name
        self.host = host
        self.port = port
        self.is_current_agent = is_current_agent


class TeamConfig:
    def __init__(self, agents: List[AgentConfig]):
        self.agents = agents

    def get_current_agent(self) -> Optional[AgentConfig]:
        """Returns the agent marked as current agent, or None if not found."""
        return next((agent for agent in self.agents if agent.is_current_agent), None)


def load_team_config(config_path: str = "team-config.json") -> TeamConfig:
    """
    Loads the team configuration from the specified JSON file.

    Args:
        config_path: Path to the team configuration JSON file.
                    If None, defaults to 'team-config.json' in the project root directory.

    Returns:
        TeamConfig object containing agent configurations
    """
    if not config_path:
        # Default to project root directory (one level up from agent directory)
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(base_dir, 'team-config.json')

    try:
        with open(config_path, 'r') as f:
            config_data = json.load(f)

        # Parse agent configurations
        agent_configs = []

        for agent_data in config_data.get('agents', []):
            agent = AgentConfig(
                name=agent_data.get('name', 'Claude'),
                host=agent_data.get('host', '127.0.0.1'),
                port=agent_data.get('port', 8081),
                is_current_agent=agent_data.get('isCurrentAgent', False)
            )
            agent_configs.append(agent)

        return TeamConfig(agent_configs)

    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        print(f"Error loading team configuration: {e}")
        # Return an empty configuration if the file cannot be loaded
        return TeamConfig([])


def get_team_config() -> TeamConfig:
    """
    Loads the team configuration and stores it in the cache.

    Returns:
        The TeamConfig, either from the cache or newly loaded.
    """
    global TEAM_CONFIG
    if TEAM_CONFIG is None:
        TEAM_CONFIG = load_team_config()
    return TEAM_CONFIG


def get_current_agent_name() -> str:
    """
    Returns the name of the current agent as specified in the team configuration.

    Returns:
        The name of the current agent, or Claude if not found.
    """
    current_agent = get_team_config().get_current_agent()
    return current_agent.name if current_agent else "Claude"


def get_agent_endpoints() -> dict[str, str]:
    """
    Returns a dictionary mapping agent names to their API endpoints.
    """
    team_config = get_team_config()
    endpoints = {}

    for agent in team_config.agents:
        endpoint = f"http://{agent.host}:{agent.port}"
        endpoints[agent.name] = endpoint

    return endpoints
