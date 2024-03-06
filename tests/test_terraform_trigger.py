import json
from base64 import urlsafe_b64encode
from typing import Any

from cloudevents.http import CloudEvent

from multani.models import TerraformCloudTriggerAllRequest


def json_b64(value: Any) -> str:
    data = json.dumps(value).encode("utf-8")
    return urlsafe_b64encode(data).decode("utf-8")


def create_cloud_event(payload: Any) -> CloudEvent:
    data = {
        "message": {
            "@type": "type.googleapis.com/google.pubsub.v1.PubsubMessage",
            "data": json_b64(payload),
            "attributes": {},
            "messageId": "1",
            "publishTime": "2023-04-16T12:23:47.225222Z",
        }
    }
    attributes = {
        "Content-Type": "application/json",
        "source": "from-galaxy-far-far-away",
        "type": "cloudevent.greet.you",
    }
    event = CloudEvent(attributes, data)

    return event


def test_parse_terraform_trigger_request() -> None:
    payload = {
        "organization": "test",
        "secret_name": "some/secret",
        "tags_included": [],
        "tags_excluded": ["ignore"],
    }
    event = create_cloud_event(payload)

    m = TerraformCloudTriggerAllRequest.from_cloud_event(event)
    assert m.organization == "test"
    assert m.tags_included == []
    assert m.tags_excluded == ["ignore"]
