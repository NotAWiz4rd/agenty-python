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

    def __str__(self):
        return f"AgentConfig(name={self.name}, host={self.host}, port={self.port}, is_current_agent={self.is_current_agent})"


class TeamConfig:
    def __init__(self, agents: List[AgentConfig]):
        self.agents = agents

    def __str__(self):
        return f"TeamConfig(agents={[str(agent) for agent in self.agents]})"

    def get_current_agent(self) -> Optional[AgentConfig]:
        """Returns the agent marked as current agent, or None if not found."""
        return next((agent for agent in self.agents if agent.is_current_agent), None)


# Cache for the team configuration to avoid reloading it multiple times
TEAM_CONFIG: Optional[TeamConfig] = None


def load_team_config(
        config_path: str = "team-config.json",
        docker_mode: bool = False,
        docker_agent_index: Optional[int] = None,
        docker_host_base: Optional[str] = None,
) -> TeamConfig:
    """
    Loads the team configuration from the specified JSON file.

    Args:
        config_path: Path to the team configuration JSON file.
                    If None, defaults to 'team-config.json' in the project root directory.
        docker_mode: If True, overrides the current agent based on the docker_agent_index.
        docker_agent_index: The index of the agent in Docker mode to be set as the current agent.
        docker_host_base: The base host for Docker mode (e.g., 'container_base_name').

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

        for agent_index, agent_data in enumerate(config_data.get('agents', [])):
            is_current_agent = agent_data.get('isCurrentAgent', False)

            if docker_mode and docker_agent_index is not None:
                # Override isCurrentAgent in Docker mode using the docker_agent_index
                is_current_agent = agent_index == docker_agent_index

            host = agent_data.get('host', '127.0.0.1')
            if docker_mode and docker_host_base is not None:
                # Override host in Docker mode using the docker_host_base for other agents
                host = f"{docker_host_base}-{agent_index + 1}" if not is_current_agent else "0.0.0.0"

            # Always use port 8000 for the current agent in Docker mode, otherwise use the specified port
            port = 8000 if docker_mode else agent_data.get('port', 8081)

            agent_configs.append(AgentConfig(
                is_current_agent=is_current_agent,
                name=agent_data.get('name', 'Claude'),
                host=host,
                port=port,
            ))

        team_config = TeamConfig(agent_configs)
        print(f"Loaded team configuration: {team_config}")
        return team_config

    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        print(f"Error loading team configuration: {e}")
        # Return an empty configuration if the file cannot be loaded
        return TeamConfig([])


def initialize_team_config(
        docker_mode: bool = False,
        docker_agent_index: Optional[int] = None,
        docker_host_base: Optional[str] = None,
) -> TeamConfig:
    """
    Loads the team configuration and stores it in the cache.

    Args:
        docker_mode: If True, overrides the current agent based on the docker_agent_index.
        docker_agent_index: The index of the agent in Docker mode to be set as the current agent.
        docker_host_base: The base host for Docker mode (e.g., 'container_base_name').

    Returns:
        The TeamConfig, either from the cache or newly loaded.
    """
    global TEAM_CONFIG
    if TEAM_CONFIG is None:
        TEAM_CONFIG = load_team_config(
            docker_mode=docker_mode,
            docker_agent_index=docker_agent_index,
            docker_host_base=docker_host_base,
        )

    return TEAM_CONFIG


def get_team_config() -> TeamConfig:
    """
    Retrieves the team configuration from the cache.

    Returns:
        The loaded TeamConfig, or raises an error.
    """
    global TEAM_CONFIG
    if TEAM_CONFIG is not None:
        return TEAM_CONFIG

    raise ValueError("Team configuration has not been initialized. Call initialize_team_config() first.")


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
        if not agent.is_current_agent:
            endpoint = f"http://{agent.host}:{agent.port}"
            endpoints[agent.name] = endpoint

    return endpoints
