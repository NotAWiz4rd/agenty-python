#!/bin/bash

# Set your remote repo path here
USERNAME="XXXXXXXXX"
PATH_TO_REPO="XXXXX/XXXXXX" # Adjust this path as needed
REPO_URL="/Users/$USERNAME/$PATH_TO_REPO"

# Set the local directory name. If not set, git will use the repo name.
LOCAL_DIR="work_repo"

if [ -z "$LOCAL_DIR" ]; then
  git clone "$REPO_URL"
else
  git clone "$REPO_URL" "$LOCAL_DIR"
fi

echo "Repository cloned successfully!"

