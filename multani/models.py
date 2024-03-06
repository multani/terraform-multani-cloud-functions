from base64 import urlsafe_b64decode
from typing import Self

from cloudevents.http import CloudEvent
from pydantic import BaseModel


class TerraformCloudTriggerAllRequest(BaseModel):
    organization: str
    secret_name: str
    tags_included: list[str] = []
    tags_excluded: list[str] = []

    @classmethod
    def from_cloud_event(cls, event: CloudEvent) -> Self:
        """Parse a request from a Cloud Event message"""

        raw_data = event.data["message"]["data"]
        data = urlsafe_b64decode(raw_data).decode("utf-8")
        obj = cls.model_validate_json(data)

        return obj
