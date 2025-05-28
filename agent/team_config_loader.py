#!/usr/bin/env python3
import json
import os
from typing import List, Optional


class AgentConfig:
    def __init__(self, name: str, host: str, port: int, is_current_agent: bool):
        self.name = name
        self.host = host
        self.port = port
        self.is_current_agent = is_current_agent


class TeamConfig:
    def __init__(self, agents: List[AgentConfig], current_agent: Optional[AgentConfig] = None):
        self.agents = agents
        # Set current_agent to the agent with isCurrentAgent=True, or None if not found
        self.current_agent = current_agent or next((agent for agent in agents if agent.is_current_agent), None)

    def get(self, param, param1):
        pass


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
        current_agent = None

        for agent_data in config_data.get('agents', []):
            agent = AgentConfig(
                name=agent_data.get('name', ''),
                host=agent_data.get('host', 'http://0.0.0.0'),
                port=agent_data.get('port', 8000),
                is_current_agent=agent_data.get('isCurrentAgent', True)
            )
            agent_configs.append(agent)

            if agent.is_current_agent:
                current_agent = agent

        return TeamConfig(agent_configs, current_agent)

    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        print(f"Error loading team configuration: {e}")
        # Return an empty configuration if the file cannot be loaded
        return TeamConfig([])


def get_current_agent_name() -> Optional[str]:
    """
    Returns the name of the current agent as specified in the team configuration.

    Returns:
        The name of the current agent, or None if not found.
    """
    config = load_team_config()
    if config.current_agent:
        return config.current_agent.name
    return None


def get_current_agent_port() -> int:
    """
    Returns the port of the current agent as specified in the team configuration.

    Returns:
        The port of the current agent, or 8000 if not found.
    """
    config = load_team_config()
    if config.current_agent:
        return config.current_agent.port
    return 8000
