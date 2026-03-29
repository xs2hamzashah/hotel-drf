from .settings import *  # noqa

# Local variant with stricter host allowance (no implicit localhost).
# Override any env-provided value if desired.
ALLOWED_HOSTS = []

# Keep DEBUG behavior from base settings (defaults to True unless env overrides).
