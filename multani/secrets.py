import os

import structlog
from google.cloud import secretmanager

from .tracing import get_tracer

LOGGER = structlog.get_logger()


_CACHED_SECRETS: dict[str, str] = {}


def fetch_secret(secret_name: str):
    logger = LOGGER.bind(secret=secret_name)
    tracer = get_tracer(__name__)

    logger.info(f"Fetching token from Secret Manager {secret_name!r}")

    with tracer.start_as_current_span("Secret: fetch version") as span:
        span.set_attribute("secret-name", secret_name)
        secrets = secretmanager.SecretManagerServiceClient()
        secret = secrets.access_secret_version(name=secret_name)

    payload = secret.payload.data.decode("utf-8")
    logger.info("Secret payload fetched")

    return payload


def fetch_secret_from_env(env_var_name: str) -> str:
    logger = LOGGER.bind(env_var=env_var_name)
    tracer = get_tracer(__name__)

    if env_var_name not in os.environ:
        logger.critical(f"Environment variable {env_var_name!r} not set.")
        raise RuntimeError(f"Unable to load secret using {env_var_name!r}")

    with tracer.start_as_current_span("Secret: fetch from env") as span:
        span.set_attribute("env-var", env_var_name)

        secret_key = os.environ[env_var_name]
        logger.debug(f"Secret key is {secret_key}")

        if secret_key in _CACHED_SECRETS:
            logger.debug("Fetching cached secret value")
            value = _CACHED_SECRETS[secret_key]
        else:
            value = fetch_secret(secret_key)
            logger.debug("Caching secret")
            _CACHED_SECRETS[secret_key] = value

        return value
