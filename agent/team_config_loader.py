#!/usr/bin/env python3
import json
import os
from typing import List, Optional


# Cache for the team configuration to avoid reloading it multiple times
_TEAM_CONFIG_CACHE = None

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


def load_team_config(config_path: str = None) -> TeamConfig:
    """
    Loads the team configuration from the specified JSON file.

    Args:
        config_path: Path to the team configuration JSON file.
                    If None, defaults to 'team-config.json' in the project root directory.

    Returns:
        TeamConfig object containing agent configurations
    """
    if config_path is None:
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
                name=agent_data.get('name', ''),
                host=agent_data.get('host', 'http://0.0.0.0'),
                port=agent_data.get('port', 8000),
                is_current_agent=agent_data.get('isCurrentAgent', True)
            )
            agent_configs.append(agent)

        return TeamConfig(agent_configs)

    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        print(f"Error loading team configuration: {e}")
        # Return an empty configuration if the file cannot be loaded
        return TeamConfig([])



def _get_cached_team_config() -> TeamConfig:
    """
    Loads the team configuration and stores it in the cache.

    Returns:
        The TeamConfig, either from the cache or newly loaded.
    """
    global _TEAM_CONFIG_CACHE
    if _TEAM_CONFIG_CACHE is None:
        _TEAM_CONFIG_CACHE = load_team_config()
    return _TEAM_CONFIG_CACHE


def get_current_agent_name() -> Optional[str]:
    """
    Returns the name of the current agent as specified in the team configuration.

    Returns:
        The name of the current agent, or None if not found.
    """
    config = _get_cached_team_config()
    current_agent = config.get_current_agent()
    if current_agent:
        return current_agent.name
    return "Claude" # Default name if not found


def get_current_agent_port() -> int:
    """
    Returns the port of the current agent as specified in the team configuration.

    Returns:
        The port of the current agent, or 8000 if not found.
    """
    config = _get_cached_team_config()
    current_agent = config.get_current_agent()
    if current_agent:
        return current_agent.port
    return 8000


def is_team_mode() -> bool:
    """
    Checks if the application is running in team mode (multiple agents).

    Returns:
        True if multiple agents are defined in the configuration, False otherwise.
    """
    config = _get_cached_team_config()
    return len(config.agents) > 1


def clear_config_cache():
    """
    Clears the configuration cache to force reloading of the configuration.
    Useful for testing or when the configuration may change during runtime.
    """
    global _TEAM_CONFIG_CACHE
    _TEAM_CONFIG_CACHE = None