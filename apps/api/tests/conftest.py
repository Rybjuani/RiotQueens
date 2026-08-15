"""Legacy domain tests run against the explicit pre-auth compatibility mode.

Authentication regressions switch the setting back on and inject a verifier;
no CI test calls Auth0.
"""

import os

os.environ.setdefault("RIOTQUEENS_AUTH_ENABLED", "false")
