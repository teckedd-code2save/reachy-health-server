#!/bin/zsh
# Usage:
#   ./commit.sh "Your commit message"        # Normal commit & push
#   ./commit.sh --init "Your commit message" # First push: init, add remote, push

if [ "$1" = "--init" ]; then
  if [ -z "$2" ]; then
    echo "Usage: $0 --init 'commit message'"
    exit 1
  fi
  git init
  git add .
  git commit -m "$2"
  git branch -M main
  git remote add origin https://github.com/teckedd-code2save/reachy-health-server.git
  git push -u origin main
else
  if [ -z "$1" ]; then
    echo "Usage: $0 'commit message'"
    exit 1
  fi
  git add .
  git commit -m "$1"
  git push --set-upstream origin main
fi
