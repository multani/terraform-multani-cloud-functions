import asyncio

import httpx
import structlog

from ..http import check_status_json
from ..tracing import get_tracer
from .models import ListWorkspacesResponse
from .models import RunCreateRequest
from .models import RunCreateResponse
from .models import Workspace

LOGGER = structlog.get_logger()
TF_CLOUD_BASE = "https://app.terraform.io"
TF_CLOUD_API = f"{TF_CLOUD_BASE}/api/v2"


class TerraformCloud:
    def __init__(self, http: httpx.AsyncClient, token: str):
        self.http = http
        self.token = token

        self.logger = LOGGER.bind()
        self.tracer = get_tracer(__name__)

        http.headers["Content-Type"] = "application/vnd.api+json"
        if token:
            http.headers["Authorization"] = f"Bearer {token}"

    async def trigger_all(
        self,
        org: str,
        includes: list[str],
        excludes: list[str],
    ) -> bool:
        with self.tracer.start_span("Terraform Cloud: trigger all workspaces") as span:
            span.set_attribute("tfcloud.organization_name", org)

            workspaces = await self.fetch_workspaces(org, includes, excludes)

            http_limiter = asyncio.Semaphore(3)

            async def trigger(org: str, name: str, id: str) -> None:
                logger = self.logger.bind(org=org, workspace=name, workspace_id=id)
                try:
                    async with http_limiter:
                        await self.workspace_create_run(org, name, id)
                except Exception as exc:
                    logger.exception("Error while creating workspace run")
                    raise

            awaitables = [trigger(org, ws.attributes.name, ws.id) for ws in workspaces]
            results = await asyncio.gather(*awaitables, return_exceptions=True)

            for r, ws in zip(results, workspaces):
                if isinstance(r, BaseException):
                    self.logger.error("At least one trigger didn't work successfully.")
                    return False

            self.logger.info("All triggers completed successfully.")
            return True

    async def fetch_workspaces(
        self,
        org: str,
        includes: list[str],
        excludes: list[str],
    ) -> list[Workspace]:
        with self.tracer.start_as_current_span(
            "Terraform Cloud: get workspaces"
        ) as span:
            span.set_attribute("tfcloud.organization_name", org)

            self.logger.info("Fetching the list of workspaces")

            # https://www.terraform.io/cloud-docs/api-docs/workspaces#list-workspaces
            # TODO: implement paging
            url = f"{TF_CLOUD_API}/organizations/{org}/workspaces"
            r = await self.http.get(url)
            check_status_json(r)

            response = ListWorkspacesResponse.model_validate_json(r.text)
            discovered = response.data
            self.logger.debug(
                f"Fetched {len(discovered)} workspaces, applying filters..."
            )

            workspaces = []

            for workspace in discovered:
                name = workspace.attributes.name
                tags = workspace.attributes.tag_names

                # "remote" means "executed by Terraform Cloud"
                # https://www.terraform.io/cloud-docs/workspaces/settings#execution-mode
                if workspace.attributes.execution_mode != "remote":
                    self.logger.debug(
                        f"workspace {name!r} doesn't execute remotely, skipping"
                    )
                    continue

                if any(t in tags for t in excludes):
                    # Workspaces containing this tag were explicitly filtered-out.
                    excluded = ", ".join(sorted(excludes))
                    self.logger.debug(
                        f"workspace {name!r} filtered out by tag: {excluded}"
                    )
                    continue

                if includes:
                    if set(includes).issubset(set(tags)):
                        included = ", ".join(sorted(includes))
                        self.logger.debug(
                            f"workspace {name!r} selected by tags: {included}"
                        )
                        workspaces.append(workspace)
                        continue

                else:
                    self.logger.debug(f"workspace {name!r} selected")
                    workspaces.append(workspace)

            self.logger.info(f"Found {len(workspaces)} matching workspaces")

            return workspaces

    async def workspace_create_run(
        self,
        org: str,
        ws_name: str,
        ws_id: str,
    ) -> str | None:
        logger = self.logger.bind(
            workspace=ws_name, workspace_id=ws_id, organization=org
        )
        with self.tracer.start_as_current_span("Terraform Cloud: create run") as span:
            span.set_attribute("tfcloud.workspace_name", ws_name)
            span.set_attribute("tfcloud.workspace_id", ws_id)
            span.set_attribute("tfcloud.organization_name", org)

            logger.info(f"Triggering plan for workspace {ws_name!r} (ID={ws_id})")

            # https://www.terraform.io/cloud-docs/api-docs/run#create-a-run
            url = f"{TF_CLOUD_API}/runs"
            request = RunCreateRequest.create(ws_id, "Auto-trigger")

            r = await self.http.post(url, json=request.model_dump())
            try:
                check_status_json(r)
            except httpx.HTTPStatusError as exc:
                logger.exception(
                    f"Unable to trigger workspace {ws_name}: {str(exc)}", exception=exc
                )
                return None

            response = RunCreateResponse.model_validate_json(r.text)

            run_id = response.data.id
            link = f"{TF_CLOUD_BASE}/app/{org}/workspaces/{ws_name}/runs/{run_id}"

            logger.info(f"Run triggered at: {link}")
            return link
