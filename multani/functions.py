import asyncio
import json
from base64 import urlsafe_b64decode
from typing import Any

import httpx
import structlog
from flask import Request
from flask import Response
from flask.typing import ResponseReturnValue

from multani import secrets
from multani import tracing
from multani.google.models import ErrorReporting
from multani.slack import SlackClient
from multani.tfcloud import TerraformCloud

from . import functions_framework

LOGGER = structlog.get_logger()


def terraform_cloud_trigger_all(event, context):
    tracer = tracing.get_tracer(__name__)
    logger = LOGGER.bind(function="trigger_all_handler")

    logger.info("Fetching parameters from event")
    data = json.loads(urlsafe_b64decode(event["data"]).decode("utf-8"))

    if "organization" not in data:
        raise ValueError("must pass an 'organization' as input")

    organization = data["organization"]

    included = data.get("tags_included", [])
    excluded = data.get("tags_excluded", [])

    if "secret_name" not in data:
        raise ValueError("must pass a 'secret_name' as input")

    secret_name = data["secret_name"]
    token = secrets.fetch_secret(secret_name)

    with tracer.start_as_current_span("func: trigger all"):
        http = httpx.AsyncClient()
        tfcloud = TerraformCloud(http, token)
        task = tfcloud.trigger_all(organization, included, excluded)
        asyncio.run(task)


# https://api.slack.com/apps/A069JJT5QMS/
@functions_framework.http
def error_reporting_slack(request: Request) -> ResponseReturnValue:
    channel_id = "C04U6S229S4"
    tracer = tracing.get_tracer(__name__)
    logger = LOGGER.bind(function="error_reporting_slack")

    expected_auth_token = secrets.fetch_secret_from_env("SECRET_HTTP_AUTH_TOKEN")
    if request.args.get("auth_token") != expected_auth_token:
        return Response("Forbidden", 403)

    logger.debug("HTTP request", headers=request.headers, data=request.data)

    content_type = request.headers["content-type"]
    if content_type != "application/json":
        logger.critical(
            f"Expected `application/json` content-type, got: `{content_type}`"
        )
        return Response("Invalid", 400)

    token = secrets.fetch_secret_from_env("SECRET_SLACK_API_TOKEN")
    client = SlackClient(token)

    if (
        request.json is not None and request.json["version"] == "test"
    ):  # testing the webhook
        # The payload when called for testing is an Incident object, not an
        # Error Reporting object.
        logger.info("Received a test notification")
        text = "Testing the notification channel :wave:"
        client.post_message(channel_id, text=text, icon_emoji="📞")
        return ("OK", 200)

    with tracer.start_as_current_span("Error Reporting: parse"):
        error = ErrorReporting.from_request(request)

    blocks: list[dict[Any, Any]] = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"🚨 {error.subject}",
                "emoji": True,
            },
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Type:*\n`{error.exception_info.type}`",
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Message:*\n{error.exception_info.message}",
                },
                {
                    "type": "mrkdwn",
                    "text": f"<{error.group_info.detail_link}|ℹ️  View error>",
                },
            ],
        },
        {
            "type": "rich_text",
            "elements": [
                {
                    "type": "rich_text_preformatted",
                    "elements": [
                        {
                            "type": "text",
                            "text": error.event_info.log_message,
                        },
                    ],
                },
            ],
        },
    ]

    logger.info("Posting error to Slack")
    client.post_message(channel_id, blocks=blocks, icon_emoji="🚨")
    logger.info("Error posted to Slack")

    return Response("Error sent to Slack", 200)
