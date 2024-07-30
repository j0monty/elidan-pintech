#!/usr/bin/env bash
# Assumes it's being run from repository root!

# This sets the $PYTHONPATH variable in your local .env to allow an IDE to inspect first-party code.
# It collects all of the source roots from Pants and appends them to the PYTHONPATH.
# Preseves existing contents and only writes to .env if there are changes.
set -eux

export ROOTS="$(./pants roots --roots-sep=' ')"
python3 -c '
from os import environ
from pathlib import Path

env_fp = Path(".env")
if env_fp.exists():
    lines = env_fp.read_text().splitlines()
else:
    lines = []

roots = environ["ROOTS"].split(" ")
paths = [f"./{root}" for root in roots]
paths.append("$PYTHONPATH")
paths_str = ":".join(paths)
new_line = f"PYTHONPATH=\"{paths_str}\""

if new_line not in lines:
    lines.append(new_line)
    env_fp.write_text("\n".join(lines))
'
