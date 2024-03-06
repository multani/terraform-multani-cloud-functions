import asyncio
import os
from typing import Any

import httpx
import structlog
from cloudevents.http.event import CloudEvent
from flask import Request
from flask import Response
from flask.typing import ResponseReturnValue

from multani import secrets
from multani import tracing
from multani.google.models import ErrorReporting
from multani.google.models import is_test_notification
from multani.http import check_authorization
from multani.slack import SlackClient
from multani.tfcloud import TerraformCloud

from . import functions_framework
from .models import TerraformCloudTriggerAllRequest

LOGGER = structlog.get_logger()


@functions_framework.cloud_event
def terraform_cloud_trigger_all(event: CloudEvent) -> None:
    tracer = tracing.get_tracer(__name__)
    logger = LOGGER.bind(function="trigger_all_handler")

    logger.info("Fetching parameters from event")

    request = TerraformCloudTriggerAllRequest.from_cloud_event(event)
    token = secrets.fetch_secret(request.secret_name)

    with tracer.start_as_current_span("func: trigger all"):
        http = httpx.AsyncClient()
        tfcloud = TerraformCloud(http, token)
        task = tfcloud.trigger_all(
            request.organization,
            request.tags_included,
            request.tags_excluded,
        )
        asyncio.run(task)


# https://api.slack.com/apps/A069JJT5QMS/
@functions_framework.http
def error_reporting_slack(request: Request) -> ResponseReturnValue:
    channel_id = os.environ["SLACK_CHANNEL_ID"]

    tracer = tracing.get_tracer(__name__)
    logger = LOGGER.bind(function="error_reporting_slack")

    logger.debug(
        "HTTP request", headers=request.headers, data=request.data, args=request.args
    )

    username = os.environ["HTTP_AUTH_USERNAME"]
    password = secrets.fetch_secret_from_env("SECRET_HTTP_AUTH_PASSWORD")
    check_authorization(request, username, password)

    logger.debug("HTTP request", headers=request.headers, data=request.data)

    token = secrets.fetch_secret_from_env("SECRET_SLACK_API_TOKEN")
    client = SlackClient(token)

    with tracer.start_as_current_span("Error Reporting: parse"):
        try:
            error = ErrorReporting.from_request(request)
        except:  # Try to parse it as a test notification? # noqa: E722
            if not is_test_notification(request):
                raise

            # The webhook is being tested ...
            # The payload used during the test notification is an Incident
            # object, not an Error Reporting object...
            logger.info("Received a test notification")
            text = "Testing the notification channel :wave:"
            client.post_message(channel_id, text=text, icon_emoji="📞")
            return ("OK", 200)

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
