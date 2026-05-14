#!/bin/bash
# scripts/rollback.sh
# Rollback docker-compose containers by checking out a previous tag/commit and rebuilding.

set -e

if [ -z "$1" ]; then
    echo "Usage: ./rollback.sh <git_tag_or_commit>"
    echo "Example: ./rollback.sh v1.0.1"
    exit 1
fi

TAG=$1
echo "Rolling back infrastructure to $TAG..."

# Checkout the previous stable code
git checkout $TAG

# Rebuild and restart the containers
docker-compose down
docker-compose build
docker-compose up -d

echo "Rollback to $TAG complete. The system is now running the older version."
