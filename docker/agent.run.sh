ip=$(ip addr show eth0 | grep 'inet ' | awk '{print $2}' | cut -d/ -f1)
hostname=$(dig -x $ip +short | cut -d'.' -f1)
host_index=$(echo $hostname | sed 's/.*-//')
export agent_index=$((host_index - 1))

echo "Starting agent with index: $agent_index"
python main.py
