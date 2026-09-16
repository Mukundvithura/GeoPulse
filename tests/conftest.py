"""Import paths for the test suite.

Nothing here is installed as a package, so the tests put the two import roots
the app itself uses on sys.path:

  repo root   -- for `api.main` and the shared `config` module
  collector/  -- the collectors are scripts, not a package; gdelt_collector
                 does a bare `from fips_iso import ...` that only resolves
                 with collector/ on the path, exactly as it does when run as
                 `python collector/gdelt_collector.py`

No test in this suite touches Postgres, Ollama or Memgraph. Both modules under
test connect lazily inside functions, so importing them needs no services.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

for path in (ROOT, ROOT / "collector"):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))
