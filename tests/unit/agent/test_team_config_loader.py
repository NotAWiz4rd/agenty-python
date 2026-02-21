"""Unit tests for agent/team_config_loader.py"""
import json

import pytest

import team_config_loader
from team_config_loader import AgentConfig, TeamConfig, get_agent_endpoints, load_team_config


@pytest.fixture(autouse=True)
def reset_team_config_cache():
    """Reset global TEAM_CONFIG cache before and after each test."""
    team_config_loader.TEAM_CONFIG = None
    yield
    team_config_loader.TEAM_CONFIG = None


# ---------------------------------------------------------------------------
# load_team_config
# ---------------------------------------------------------------------------

class TestLoadTeamConfig:
    def test_parses_valid_json_returns_team_config(self, team_config_file):
        config = load_team_config(str(team_config_file))
        assert isinstance(config, TeamConfig)
        assert len(config.agents) == 2

    def test_agent_names_loaded_correctly(self, team_config_file):
        config = load_team_config(str(team_config_file))
        names = {a.name for a in config.agents}
        assert names == {"Claude", "Carmen"}

    def test_current_agent_flag_loaded(self, team_config_file):
        config = load_team_config(str(team_config_file))
        current = config.get_current_agent()
        assert current is not None
        assert current.name == "Claude"

    def test_missing_file_returns_empty_config(self, tmp_path):
        config = load_team_config(str(tmp_path / "missing.json"))
        assert isinstance(config, TeamConfig)
        assert config.agents == []

    def test_malformed_json_returns_empty_config(self, tmp_path):
        bad_file = tmp_path / "bad.json"
        bad_file.write_text("not valid json {{{{")
        config = load_team_config(str(bad_file))
        assert isinstance(config, TeamConfig)
        assert config.agents == []

    def test_port_loaded_from_config(self, team_config_file):
        config = load_team_config(str(team_config_file))
        claude = next(a for a in config.agents if a.name == "Claude")
        assert claude.port == 8081


# ---------------------------------------------------------------------------
# TeamConfig.get_current_agent
# ---------------------------------------------------------------------------

class TestGetCurrentAgent:
    def test_returns_current_agent(self):
        agents = [
            AgentConfig(name="Alice", host="localhost", port=8081, is_current_agent=True),
            AgentConfig(name="Bob", host="localhost", port=8082, is_current_agent=False),
        ]
        config = TeamConfig(agents)
        current = config.get_current_agent()
        assert current is not None
        assert current.name == "Alice"

    def test_returns_none_when_no_current_agent(self):
        agents = [
            AgentConfig(name="Alice", host="localhost", port=8081, is_current_agent=False),
            AgentConfig(name="Bob", host="localhost", port=8082, is_current_agent=False),
        ]
        config = TeamConfig(agents)
        current = config.get_current_agent()
        assert current is None

    def test_returns_none_for_empty_config(self):
        config = TeamConfig([])
        assert config.get_current_agent() is None


# ---------------------------------------------------------------------------
# get_agent_endpoints
# ---------------------------------------------------------------------------

class TestGetAgentEndpoints:
    def _setup_team_config(self):
        team_config_loader.TEAM_CONFIG = TeamConfig([
            AgentConfig(name="Alice", host="localhost", port=8081, is_current_agent=True),
            AgentConfig(name="Bob", host="remote-host", port=8082, is_current_agent=False),
            AgentConfig(name="Carol", host="other-host", port=8083, is_current_agent=False),
        ])

    def test_excludes_current_agent(self):
        self._setup_team_config()
        endpoints = get_agent_endpoints()
        assert "Alice" not in endpoints

    def test_includes_non_current_agents(self):
        self._setup_team_config()
        endpoints = get_agent_endpoints()
        assert "Bob" in endpoints
        assert "Carol" in endpoints

    def test_url_format_is_http_host_port(self):
        self._setup_team_config()
        endpoints = get_agent_endpoints()
        assert endpoints["Bob"] == "http://remote-host:8082"
        assert endpoints["Carol"] == "http://other-host:8083"

    def test_empty_when_all_agents_are_current(self):
        team_config_loader.TEAM_CONFIG = TeamConfig([
            AgentConfig(name="Solo", host="localhost", port=8081, is_current_agent=True),
        ])
        endpoints = get_agent_endpoints()
        assert endpoints == {}


# ---------------------------------------------------------------------------
# Docker mode overrides
# ---------------------------------------------------------------------------

class TestDockerMode:
    def test_docker_index_0_sets_first_agent_as_current(self, team_config_file):
        config = load_team_config(
            str(team_config_file),
            docker_mode=True,
            docker_agent_index=0,
        )
        assert config.agents[0].is_current_agent is True
        assert config.agents[1].is_current_agent is False

    def test_docker_index_1_sets_second_agent_as_current(self, team_config_file):
        config = load_team_config(
            str(team_config_file),
            docker_mode=True,
            docker_agent_index=1,
        )
        assert config.agents[0].is_current_agent is False
        assert config.agents[1].is_current_agent is True

    def test_docker_mode_uses_port_8000(self, team_config_file):
        config = load_team_config(
            str(team_config_file),
            docker_mode=True,
            docker_agent_index=0,
        )
        for agent in config.agents:
            assert agent.port == 8000

    def test_docker_mode_sets_current_agent_host_to_0000(self, team_config_file):
        config = load_team_config(
            str(team_config_file),
            docker_mode=True,
            docker_agent_index=0,
            docker_host_base="agent",
        )
        current = config.get_current_agent()
        assert current.host == "0.0.0.0"

    def test_docker_mode_sets_other_agents_host_from_base(self, team_config_file):
        config = load_team_config(
            str(team_config_file),
            docker_mode=True,
            docker_agent_index=0,
            docker_host_base="agent",
        )
        carmen = next(a for a in config.agents if a.name == "Carmen")
        assert carmen.host == "agent-2"
