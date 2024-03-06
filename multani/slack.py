from typing import Any
from typing import Sequence

import structlog
from opentelemetry.trace import Status
from opentelemetry.trace import StatusCode
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_sdk.models.blocks import Block

from .tracing import get_tracer

__all__ = ["SlackApiError", "SlackClient"]


class SlackClient:
    def __init__(self, token: str) -> None:
        self.client = WebClient(token=token)
        self.logger = structlog.get_logger()
        self.tracer = get_tracer(__name__)

    def post_message(
        self,
        channel_id: str,
        blocks: str | Sequence[dict[Any, Any] | Block] | None = None,
        text: str | None = None,
        icon_emoji: str | None = None,
    ) -> None:
        """Post a Slack message.

        See: https://api.slack.com/methods/chat.postMessage
        """

        logger = self.logger.bind(slack_channel_id=channel_id)

        if blocks is None and text is None:
            raise ValueError("Need one of `blocks` or `text`")

        if blocks is not None and text is not None:
            raise ValueError("Need one of `blocks` or `text`")

        with self.tracer.start_as_current_span("Slack: post message") as span:
            span.set_attribute("slack-channel-id", channel_id)
            logger.debug("Posting message to Slack")
            try:
                response = self.client.chat_postMessage(
                    channel=channel_id,
                    text=text,
                    blocks=blocks,
                    icon_emoji=icon_emoji,
                )
            except SlackApiError as exc:
                logger.exception("Unable to send Slack message", exception=exc)
                span.set_status(Status(StatusCode.ERROR))
                span.record_exception(exc)
                raise exc from None

            logger.debug("Slack response", slack_response=response.data)
