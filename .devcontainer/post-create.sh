#!/bin/sh

set -eu

task env

# Hatch's default path includes a hash of the project location. Give IDEs a
# stable path without changing where Hatch stores the environment itself.
environment_path=$(hatch env find dev)
environment_link_dir="$HOME/.local/share/cloup"

mkdir -p "$environment_link_dir"
ln -sfnT "$environment_path" "$environment_link_dir/dev"
