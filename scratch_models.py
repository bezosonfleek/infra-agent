"""Scratch script: turn real `docker inspect` output into a Bundle and print it.

Run it from the project root:

    docker inspect panic-room-api-1 | PYTHONPATH=src python3 scratch_models.py

Optionally add logs:

    docker logs --tail 50 panic-room-api-1 > /tmp/logs.txt 2>&1
    docker inspect panic-room-api-1 | PYTHONPATH=src python3 scratch_models.py /tmp/logs.txt
"""

import json
import sys

from infra_agent.models import Bundle

logs = open(sys.argv[1]).read() if len(sys.argv) > 1 else ""
bundle = Bundle.from_inspect(json.load(sys.stdin), logs)

print(bundle)
