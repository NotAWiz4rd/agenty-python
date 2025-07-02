#!/bin/bash

agent_count=$(jq '.agents | length' team-config.json)
docker compose -f docker-compose.yaml up -d --scale agent=$agent_count --build
