"""Shared configuration.

One module-level read of the environment, so the API and the collectors can
never drift apart on where Postgres lives.

Override with the GEOPULSE_DB_URL environment variable. The default needs no
env setup at all and points at the docker-compose database on port 6543 --
that port is deliberate, it keeps a local Postgres on 5432 out of the way.
"""

import os

DB_URL = os.environ.get(
    "GEOPULSE_DB_URL",
    "postgresql://geopulse:geopulse@localhost:6543/geopulse",
)
