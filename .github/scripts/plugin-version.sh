#!/usr/bin/env bash
# Prints the plugin version after checking that every manifest field agrees.
# Usage: plugin-version.sh [git-ref]  (reads the working tree when no ref is given)
set -euo pipefail

ref="${1:-}"

read_file() {
  if [[ -n "$ref" ]]; then
    git show "$ref:$1"
  else
    cat "$1"
  fi
}

plugin=$(read_file .claude-plugin/plugin.json | jq -r '.version')
entry=$(read_file .claude-plugin/marketplace.json | jq -r '.plugins[] | select(.name == "decodo") | .version')
metadata=$(read_file .claude-plugin/marketplace.json | jq -r '.metadata.version')

if [[ "$plugin" != "$entry" || "$plugin" != "$metadata" ]]; then
  echo "::error::Plugin versions differ: plugin.json version=$plugin, marketplace.json plugins[decodo].version=$entry, marketplace.json metadata.version=$metadata" >&2
  exit 1
fi

if [[ ! "$plugin" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "::error::Plugin version '$plugin' is not MAJOR.MINOR.PATCH" >&2
  exit 1
fi

echo "$plugin"
