#!/bin/sh

set -eu

task env

# Hatch keeps its environments outside the repository, but editors only select
# an interpreter by themselves when it sits inside the workspace, so link it
# here. The link is ignored by Git and points nowhere outside the container.
ln -sfnT "$(hatch env find dev)" .dev-container-venv
