#!/bin/bash

usage() {
>&2 cat << EOF
Pauses the running agent team's work in Docker.

Usage: $0
   [ -h | --help ] Show help.
EOF
exit 1
}

while [[ $# -gt 0 ]]; do
  case $1 in
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

docker compose -f "$(dirname "$0")/../docker-compose.yaml" --profile "*" stop
