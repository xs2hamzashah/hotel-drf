from .settings import *  # noqa
import os
import dj_database_url

# Production overrides
DEBUG = False

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY must be set in production.")

allowed_hosts_env = os.getenv("ALLOWED_HOSTS", "").strip()
ALLOWED_HOSTS = allowed_hosts_env.split(",") if allowed_hosts_env else ["*"]

# Database from DATABASE_URL (e.g., Postgres)
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL must be set in production.")

DATABASES = {
    "default": dj_database_url.parse(
        DATABASE_URL,
        conn_max_age=600,
        ssl_require=True,
    )
}

# Static files (only minimal use in this API)
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Trust Vercel host for CSRF if needed later
vercel_url = os.getenv("VERCEL_URL")
if vercel_url:
    CSRF_TRUSTED_ORIGINS = [f"https://{vercel_url}"]

