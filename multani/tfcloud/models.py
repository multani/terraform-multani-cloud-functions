from typing import Self

from pydantic import BaseModel
from pydantic import Field


class WorkspaceAttribute(BaseModel):
    name: str
    tag_names: list[str] = Field(alias="tag-names")
    execution_mode: str = Field(alias="execution-mode")


class Workspace(BaseModel):
    id: str
    attributes: WorkspaceAttribute


class ListWorkspacesResponse(BaseModel):
    data: list[Workspace]


class RunCreateAttribute(BaseModel):
    message: str


class WorkspaceRelationshipData(BaseModel):
    id: str


class WorkspaceRelationship(BaseModel):
    data: WorkspaceRelationshipData


class WorkspaceRelationships(BaseModel):
    workspace: WorkspaceRelationship

    @classmethod
    def with_workspace_id(cls, id: str) -> Self:
        workspace = WorkspaceRelationship(data=WorkspaceRelationshipData(id=id))
        return cls(workspace=workspace)


class RunCreateRequestData(BaseModel):
    type: str = "runs"
    refresh: bool = True
    refresh_only: bool = Field(default=True, alias="refresh-only")
    auto_apply: bool = Field(default=False, alias="auto-apply")
    is_destroy: bool = Field(default=False, alias="is-destroy")
    attributes: RunCreateAttribute
    relationships: WorkspaceRelationships


class RunCreateRequest(BaseModel):
    data: RunCreateRequestData

    @classmethod
    def create(cls, workspace_id: str, message: str) -> Self:
        rel = WorkspaceRelationships.with_workspace_id(workspace_id)
        attrs = RunCreateAttribute(message=message)
        data = RunCreateRequestData(attributes=attrs, relationships=rel)
        return cls(data=data)


class RunCreateResponseData(BaseModel):
    id: str


class RunCreateResponse(BaseModel):
    data: RunCreateResponseData
