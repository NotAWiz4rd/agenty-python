#!/bin/bash

usage() {
>&2 cat << EOF
Deploys an agent team running in Docker.

Usage: $0
   [ -l | --with-group-work-log ] Activates the group work log.
   [ -o | --with-oversight-officer ] Activates the oversight officer.
   [ -R | --remote-repo ] Remote repository (either a bare repo, if directory, or a URL to clone).
   [ -T | --team-config ] Team configuration file (default: ./team-config.json).
   [ -h | --help ] Show help.
EOF
exit 1
}

TEAM_CONFIG="./team-config.json"
PROFILES=(agent)
REMOTE_REPO=""

while [[ $# -gt 0 ]]; do
  case $1 in
    -l | --with-group-work-log)
      PROFILES+=("group_work_log")
      shift
      ;;
    -o | --with-oversight-officer)
      PROFILES+=("oversight_officer")
      shift
      ;;
    -R | --remote-repo)
      REMOTE_REPO=$2
      shift 2
      ;;
    -T | --team-config)
      TEAM_CONFIG=$2
      shift 2
      ;;
    -h | --help)
      usage
      shift
      ;;
    --)
      shift
      break
      ;;
    *)
      >&2 echo Unsupported option: $1
      usage
      ;;
  esac
done


>&2 echo "============================================================"
>&2 echo "$(realpath $0)"
>&2 echo "PROFILES=(${PROFILES[@]})"
>&2 echo "REMOTE_REPO=${REMOTE_REPO}"
>&2 echo "TEAM_CONFIG=${TEAM_CONFIG}"

# Create bare, if not provided
if [ -z "$REMOTE_REPO" ]; then
  REMOTE_REPO="$(pwd)/agents_git_remote_tmp"
  git init --bare "$REMOTE_REPO/.git"
fi

# Clone, if not a directory
if [ ! -d "$REMOTE_REPO" ]; then
  git clone --bare "$REMOTE_REPO/.git" agents_git_remote_tmp
  REMOTE_REPO="$(pwd)/agents_git_remote_tmp"
fi

# Check if the remote repository is a bare repository
if ! git --git-dir="$REMOTE_REPO/.git" rev-parse --is-bare-repository | grep -q true; then
  echo "Error: The repository at $REMOTE_REPO is not a bare repository."
  exit 1
fi

# Undeploy the existing Docker containers, before volume creation
docker compose -f "$(dirname "$0")/../docker-compose.yaml" --profile "*" down

# Remove previous volume if it exists
if docker volume inspect agents_git_remote &>/dev/null; then
  docker volume rm agents_git_remote
fi

# Create a Docker volume that binds to the remote repository
docker volume create --opt type=none --opt o=bind --opt device="$REMOTE_REPO" agents_git_remote

# Copy the team's task to the .env file
team_task=$(jq -r '.task' $TEAM_CONFIG)
if grep -q '^INITIAL_GROUP_CHAT_MESSAGE=' "$(dirname "$0")/../.env"; then
  sed -i '' "s|^INITIAL_GROUP_CHAT_MESSAGE=.*|INITIAL_GROUP_CHAT_MESSAGE=\"$team_task\"|" "$(dirname "$0")/../.env"
else
  echo "INITIAL_GROUP_CHAT_MESSAGE=\"$team_task\"" >> "$(dirname "$0")/../.env"
fi

# Retrieve the agent count from the team configuration
agent_count=$(jq '.agents | length' $TEAM_CONFIG)
if [ "$agent_count" -lt 2 ]; then
  echo "Error: At least 2 agents are required."
  exit 1
fi

# Launch the Docker containers with the specified profiles and agent count
docker compose -f "$(dirname "$0")/../docker-compose.yaml" $(printf -- '--profile %s ' "${PROFILES[@]}") up \
  -d --scale agent=$agent_count --build --force-recreate
