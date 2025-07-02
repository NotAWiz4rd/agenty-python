#!/bin/sh

# Docker tricks to get the nice hostname
ip=$(ip addr show eth0 | grep 'inet ' | awk '{print $2}' | cut -d/ -f1)
hostname=$(dig -x $ip +short | cut -d'.' -f1)

# Extract the base host name (without the index)
base_host=$(echo $hostname | sed 's/\(.*\)-.*/\1/')

# Get the index of the host from the hostname
host_index=$(echo $hostname | sed 's/.*-//')
agent_index=$((host_index - 1))

git clone /remote /app/work_repo
python -u main.py --docker_mode True --docker_agent_index $agent_index --docker_host_base $base_host
