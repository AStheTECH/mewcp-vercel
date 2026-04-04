import json
import logging
from pathlib import Path
from typing import Any

from fastmcp import FastMCP
from pydantic import Field

from .config import DEFAULT_TIMEOUT_SECONDS, MAX_RESPONSE_BODY_CHARS
from .service import execute_vercel_request

logger = logging.getLogger("vercel-mcp-server")
ENDPOINT_CATALOG_PATH = Path(__file__).with_name("vercel_endpoints.json")


def _build_scoped_params(
    params: dict[str, Any] | None,
    team_id: str | None,
    slug: str | None,
) -> dict[str, Any]:
    request_params = dict(params or {})
    if team_id:
        request_params["teamId"] = team_id
    if slug:
        request_params["slug"] = slug
    return request_params


def _execute_tool_request(
    *,
    tool_name: str,
    auth_token: str,
    method: str,
    path: str,
    team_id: str | None = None,
    slug: str | None = None,
    headers: dict[str, str] | None = None,
    params: dict[str, Any] | None = None,
    json_body: Any | None = None,
    body: str | None = None,
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
    follow_redirects: bool = True,
    max_response_chars: int = MAX_RESPONSE_BODY_CHARS,
) -> str:
    try:
        result = execute_vercel_request(
            method=method,
            path=path,
            auth_token=auth_token,
            headers=headers,
            params=_build_scoped_params(params=params, team_id=team_id, slug=slug),
            json_body=json_body,
            body=body,
            timeout_seconds=timeout_seconds,
            follow_redirects=follow_redirects,
            max_response_chars=max_response_chars,
        )
        return json.dumps(result)
    except Exception as e:
        logger.error(f"Failed {tool_name} for '{method} {path}': {e}")
        return json.dumps({"error": str(e)})


def register_tools(mcp: FastMCP) -> None:
    @mcp.tool(
        name="health_check",
        description="Check server readiness and basic availability.",
    )
    def health_check() -> str:
        return json.dumps({"status": "ok", "server": "CL Vercel MCP Server"})

    @mcp.tool(
        name="list_vercel_api_calls",
        description="Return the full Vercel REST API call catalog extracted from docs (method, path, category, doc URL).",
    )
    def list_vercel_api_calls(
        category: str | None = Field(
            default=None,
            description="Optional category filter (for example: projects, deployments, environment, aliases)",
        )
    ) -> str:
        try:
            if not ENDPOINT_CATALOG_PATH.exists():
                return json.dumps(
                    {
                        "error": "Endpoint catalog is missing.",
                        "expected_path": str(ENDPOINT_CATALOG_PATH),
                    }
                )

            calls = json.loads(ENDPOINT_CATALOG_PATH.read_text(encoding="utf-8"))
            if category:
                normalized = category.strip().lower()
                calls = [c for c in calls if c.get("category", "").lower() == normalized]

            return json.dumps(
                {
                    "count": len(calls),
                    "category": category,
                    "calls": calls,
                }
            )
        except Exception as e:
            logger.error(f"Failed list_vercel_api_calls: {e}")
            return json.dumps({"error": str(e)})

    @mcp.tool(
        name="list_projects",
        description="List projects for the authenticated account or team.",
    )
    def list_projects(
        auth_token: str = Field(..., description="Vercel personal access token or OAuth access token"),
        team_id: str | None = Field(default=None, description="Optional teamId for team-scoped requests"),
        slug: str | None = Field(default=None, description="Optional slug for team-scoped requests"),
        params: dict[str, Any] | None = Field(default=None, description="Optional query params (limit, search, from, etc.)"),
    ) -> str:
        return _execute_tool_request(
            tool_name="list_projects",
            auth_token=auth_token,
            method="GET",
            path="/v10/projects",
            team_id=team_id,
            slug=slug,
            params=params,
        )

    @mcp.tool(
        name="get_project",
        description="Get details for a specific project by ID or name.",
    )
    def get_project(
        auth_token: str = Field(..., description="Vercel personal access token or OAuth access token"),
        id_or_name: str = Field(..., description="Project ID or project name"),
        team_id: str | None = Field(default=None, description="Optional teamId for team-scoped requests"),
        slug: str | None = Field(default=None, description="Optional slug for team-scoped requests"),
    ) -> str:
        return _execute_tool_request(
            tool_name="get_project",
            auth_token=auth_token,
            method="GET",
            path=f"/v9/projects/{id_or_name}",
            team_id=team_id,
            slug=slug,
        )

    @mcp.tool(
        name="create_project",
        description="Create a new Vercel project.",
    )
    def create_project(
        auth_token: str = Field(..., description="Vercel personal access token or OAuth access token"),
        body: dict[str, Any] = Field(..., description="Project creation payload"),
        team_id: str | None = Field(default=None, description="Optional teamId for team-scoped requests"),
        slug: str | None = Field(default=None, description="Optional slug for team-scoped requests"),
    ) -> str:
        return _execute_tool_request(
            tool_name="create_project",
            auth_token=auth_token,
            method="POST",
            path="/v11/projects",
            team_id=team_id,
            slug=slug,
            json_body=body,
        )

    @mcp.tool(
        name="update_project",
        description="Update an existing Vercel project.",
    )
    def update_project(
        auth_token: str = Field(..., description="Vercel personal access token or OAuth access token"),
        id_or_name: str = Field(..., description="Project ID or project name"),
        body: dict[str, Any] = Field(..., description="Project update payload"),
        team_id: str | None = Field(default=None, description="Optional teamId for team-scoped requests"),
        slug: str | None = Field(default=None, description="Optional slug for team-scoped requests"),
    ) -> str:
        return _execute_tool_request(
            tool_name="update_project",
            auth_token=auth_token,
            method="PATCH",
            path=f"/v9/projects/{id_or_name}",
            team_id=team_id,
            slug=slug,
            json_body=body,
        )

    @mcp.tool(
        name="list_deployments",
        description="List deployments for the authenticated account or team.",
    )
    def list_deployments(
        auth_token: str = Field(..., description="Vercel personal access token or OAuth access token"),
        team_id: str | None = Field(default=None, description="Optional teamId for team-scoped requests"),
        slug: str | None = Field(default=None, description="Optional slug for team-scoped requests"),
        params: dict[str, Any] | None = Field(default=None, description="Optional query params (limit, projectId, state, etc.)"),
    ) -> str:
        return _execute_tool_request(
            tool_name="list_deployments",
            auth_token=auth_token,
            method="GET",
            path="/v6/deployments",
            team_id=team_id,
            slug=slug,
            params=params,
        )

    @mcp.tool(
        name="get_deployment",
        description="Get deployment details by deployment ID or URL.",
    )
    def get_deployment(
        auth_token: str = Field(..., description="Vercel personal access token or OAuth access token"),
        id_or_url: str = Field(..., description="Deployment ID or deployment URL"),
        team_id: str | None = Field(default=None, description="Optional teamId for team-scoped requests"),
        slug: str | None = Field(default=None, description="Optional slug for team-scoped requests"),
    ) -> str:
        return _execute_tool_request(
            tool_name="get_deployment",
            auth_token=auth_token,
            method="GET",
            path=f"/v13/deployments/{id_or_url}",
            team_id=team_id,
            slug=slug,
        )

    @mcp.tool(
        name="create_deployment",
        description="Create a new deployment.",
    )
    def create_deployment(
        auth_token: str = Field(..., description="Vercel personal access token or OAuth access token"),
        body: dict[str, Any] = Field(..., description="Deployment creation payload"),
        team_id: str | None = Field(default=None, description="Optional teamId for team-scoped requests"),
        slug: str | None = Field(default=None, description="Optional slug for team-scoped requests"),
    ) -> str:
        return _execute_tool_request(
            tool_name="create_deployment",
            auth_token=auth_token,
            method="POST",
            path="/v13/deployments",
            team_id=team_id,
            slug=slug,
            json_body=body,
        )

    @mcp.tool(
        name="cancel_deployment",
        description="Cancel an in-progress deployment by ID.",
    )
    def cancel_deployment(
        auth_token: str = Field(..., description="Vercel personal access token or OAuth access token"),
        deployment_id: str = Field(..., description="Deployment ID"),
        team_id: str | None = Field(default=None, description="Optional teamId for team-scoped requests"),
        slug: str | None = Field(default=None, description="Optional slug for team-scoped requests"),
    ) -> str:
        return _execute_tool_request(
            tool_name="cancel_deployment",
            auth_token=auth_token,
            method="PATCH",
            path=f"/v12/deployments/{deployment_id}/cancel",
            team_id=team_id,
            slug=slug,
        )

    @mcp.tool(
        name="get_deployment_events",
        description="Get deployment event stream metadata for a deployment.",
    )
    def get_deployment_events(
        auth_token: str = Field(..., description="Vercel personal access token or OAuth access token"),
        id_or_url: str = Field(..., description="Deployment ID or deployment URL"),
        team_id: str | None = Field(default=None, description="Optional teamId for team-scoped requests"),
        slug: str | None = Field(default=None, description="Optional slug for team-scoped requests"),
        params: dict[str, Any] | None = Field(default=None, description="Optional query params for event filtering"),
    ) -> str:
        return _execute_tool_request(
            tool_name="get_deployment_events",
            auth_token=auth_token,
            method="GET",
            path=f"/v3/deployments/{id_or_url}/events",
            team_id=team_id,
            slug=slug,
            params=params,
        )

    @mcp.tool(
        name="list_project_environment_variables",
        description="List environment variables for a project.",
    )
    def list_project_environment_variables(
        auth_token: str = Field(..., description="Vercel personal access token or OAuth access token"),
        id_or_name: str = Field(..., description="Project ID or project name"),
        team_id: str | None = Field(default=None, description="Optional teamId for team-scoped requests"),
        slug: str | None = Field(default=None, description="Optional slug for team-scoped requests"),
        params: dict[str, Any] | None = Field(default=None, description="Optional query params (target, gitBranch, etc.)"),
    ) -> str:
        return _execute_tool_request(
            tool_name="list_project_environment_variables",
            auth_token=auth_token,
            method="GET",
            path=f"/v10/projects/{id_or_name}/env",
            team_id=team_id,
            slug=slug,
            params=params,
        )

    @mcp.tool(
        name="create_project_environment_variables",
        description="Create one or more environment variables for a project.",
    )
    def create_project_environment_variables(
        auth_token: str = Field(..., description="Vercel personal access token or OAuth access token"),
        id_or_name: str = Field(..., description="Project ID or project name"),
        body: dict[str, Any] | list[dict[str, Any]] = Field(
            ...,
            description="Environment variable payload",
        ),
        team_id: str | None = Field(default=None, description="Optional teamId for team-scoped requests"),
        slug: str | None = Field(default=None, description="Optional slug for team-scoped requests"),
    ) -> str:
        return _execute_tool_request(
            tool_name="create_project_environment_variables",
            auth_token=auth_token,
            method="POST",
            path=f"/v10/projects/{id_or_name}/env",
            team_id=team_id,
            slug=slug,
            json_body=body,
        )

    @mcp.tool(
        name="update_project_environment_variable",
        description="Update an existing environment variable in a project.",
    )
    def update_project_environment_variable(
        auth_token: str = Field(..., description="Vercel personal access token or OAuth access token"),
        id_or_name: str = Field(..., description="Project ID or project name"),
        environment_variable_id: str = Field(..., description="Environment variable ID"),
        body: dict[str, Any] = Field(..., description="Environment variable update payload"),
        team_id: str | None = Field(default=None, description="Optional teamId for team-scoped requests"),
        slug: str | None = Field(default=None, description="Optional slug for team-scoped requests"),
    ) -> str:
        return _execute_tool_request(
            tool_name="update_project_environment_variable",
            auth_token=auth_token,
            method="PATCH",
            path=f"/v9/projects/{id_or_name}/env/{environment_variable_id}",
            team_id=team_id,
            slug=slug,
            json_body=body,
        )

    @mcp.tool(
        name="list_project_domains",
        description="List domains assigned to a project.",
    )
    def list_project_domains(
        auth_token: str = Field(..., description="Vercel personal access token or OAuth access token"),
        id_or_name: str = Field(..., description="Project ID or project name"),
        team_id: str | None = Field(default=None, description="Optional teamId for team-scoped requests"),
        slug: str | None = Field(default=None, description="Optional slug for team-scoped requests"),
        params: dict[str, Any] | None = Field(default=None, description="Optional query params"),
    ) -> str:
        return _execute_tool_request(
            tool_name="list_project_domains",
            auth_token=auth_token,
            method="GET",
            path=f"/v9/projects/{id_or_name}/domains",
            team_id=team_id,
            slug=slug,
            params=params,
        )

    @mcp.tool(
        name="add_project_domain",
        description="Add a domain to a project.",
    )
    def add_project_domain(
        auth_token: str = Field(..., description="Vercel personal access token or OAuth access token"),
        id_or_name: str = Field(..., description="Project ID or project name"),
        body: dict[str, Any] = Field(..., description="Domain payload (typically includes name)"),
        team_id: str | None = Field(default=None, description="Optional teamId for team-scoped requests"),
        slug: str | None = Field(default=None, description="Optional slug for team-scoped requests"),
    ) -> str:
        return _execute_tool_request(
            tool_name="add_project_domain",
            auth_token=auth_token,
            method="POST",
            path=f"/v10/projects/{id_or_name}/domains",
            team_id=team_id,
            slug=slug,
            json_body=body,
        )

    @mcp.tool(
        name="assign_deployment_alias",
        description="Assign an alias to a deployment.",
    )
    def assign_deployment_alias(
        auth_token: str = Field(..., description="Vercel personal access token or OAuth access token"),
        deployment_id: str = Field(..., description="Deployment ID"),
        body: dict[str, Any] = Field(..., description="Alias payload"),
        team_id: str | None = Field(default=None, description="Optional teamId for team-scoped requests"),
        slug: str | None = Field(default=None, description="Optional slug for team-scoped requests"),
    ) -> str:
        return _execute_tool_request(
            tool_name="assign_deployment_alias",
            auth_token=auth_token,
            method="POST",
            path=f"/v2/deployments/{deployment_id}/aliases",
            team_id=team_id,
            slug=slug,
            json_body=body,
        )

    @mcp.tool(
        name="list_deployment_aliases",
        description="List aliases attached to a deployment.",
    )
    def list_deployment_aliases(
        auth_token: str = Field(..., description="Vercel personal access token or OAuth access token"),
        deployment_id: str = Field(..., description="Deployment ID"),
        team_id: str | None = Field(default=None, description="Optional teamId for team-scoped requests"),
        slug: str | None = Field(default=None, description="Optional slug for team-scoped requests"),
    ) -> str:
        return _execute_tool_request(
            tool_name="list_deployment_aliases",
            auth_token=auth_token,
            method="GET",
            path=f"/v2/deployments/{deployment_id}/aliases",
            team_id=team_id,
            slug=slug,
        )

    @mcp.tool(
        name="get_runtime_logs_for_deployment",
        description="Fetch runtime logs for a specific deployment.",
    )
    def get_runtime_logs_for_deployment(
        auth_token: str = Field(..., description="Vercel personal access token or OAuth access token"),
        project_id: str = Field(..., description="Project ID"),
        deployment_id: str = Field(..., description="Deployment ID"),
        team_id: str | None = Field(default=None, description="Optional teamId for team-scoped requests"),
        slug: str | None = Field(default=None, description="Optional slug for team-scoped requests"),
        params: dict[str, Any] | None = Field(default=None, description="Optional query params for logs (since, until, limit, etc.)"),
    ) -> str:
        return _execute_tool_request(
            tool_name="get_runtime_logs_for_deployment",
            auth_token=auth_token,
            method="GET",
            path=f"/v1/projects/{project_id}/deployments/{deployment_id}/runtime-logs",
            team_id=team_id,
            slug=slug,
            params=params,
        )

    @mcp.tool(
        name="vercel_api_request",
        description="Call any Vercel REST API endpoint with per-request tenant auth.",
    )
    def vercel_api_request(
        auth_token: str = Field(
            ...,
            description="Vercel personal access token or OAuth access token",
        ),
        method: str = Field(
            ...,
            description="HTTP method (GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS)",
        ),
        path: str = Field(
            ...,
            description="Vercel API path, for example /v10/projects or /v13/deployments",
        ),
        team_id: str | None = Field(
            default=None,
            description="Optional teamId query parameter for team-scoped requests",
        ),
        slug: str | None = Field(
            default=None,
            description="Optional slug query parameter for team-scoped requests",
        ),
        headers: dict[str, str] | None = Field(
            default=None,
            description="Optional HTTP headers merged with Authorization",
        ),
        params: dict[str, Any] | None = Field(
            default=None,
            description="Optional additional query parameters",
        ),
        json_body: Any | None = Field(
            default=None,
            description="Optional JSON request body",
        ),
        body: str | None = Field(
            default=None,
            description="Optional raw string request body",
        ),
        timeout_seconds: float = Field(
            default=DEFAULT_TIMEOUT_SECONDS,
            description="HTTP timeout in seconds",
        ),
        follow_redirects: bool = Field(
            default=True,
            description="Whether to follow HTTP redirects",
        ),
        max_response_chars: int = Field(
            default=MAX_RESPONSE_BODY_CHARS,
            description="Maximum number of response characters or bytes returned",
        ),
    ) -> str:
        return _execute_tool_request(
            tool_name="vercel_api_request",
            auth_token=auth_token,
            method=method,
            path=path,
            team_id=team_id,
            slug=slug,
            headers=headers,
            params=params,
            json_body=json_body,
            body=body,
            timeout_seconds=timeout_seconds,
            follow_redirects=follow_redirects,
            max_response_chars=max_response_chars,
        )
