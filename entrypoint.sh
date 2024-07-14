#!/bin/bash
echo 
if [[ $# -gt 0 ]]; then
  exec "$@"
else
  printf "Starting CommitCompiler Container:\n"
  sleep 1
  printf "To start run `comcom [args]`"
  sleep 1
  set -m
  tail -f /dev/null >/dev/null 2>&1
  fg %1
fi
