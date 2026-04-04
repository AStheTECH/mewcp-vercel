**Manage Vercel Projects, Deployments, Domains, and Environment Variables via MCP**

A Model Context Protocol (MCP) server that exposes Vercel's API for project lifecycle management, deployment operations, and runtime visibility.

---

## Overview

The CL Vercel MCP Server provides stateless, multi-tenant Vercel automation:

- Full Vercel API-call catalog discovery from official docs
- MVP endpoint wrappers for high-value day-to-day operations
- Generic fallback endpoint tool for uncovered API calls

Perfect for:

- CI/CD automation and deployment orchestration
- Project and environment configuration management
- Domain, alias, and runtime log troubleshooting workflows

---

## Tools

<details>
<summary><code>health_check</code> - Server readiness check</summary>

Checks basic MCP server readiness.

**Inputs:**

- None

**Output:**

```json
{
  "status": "ok",
  "server": "CL Vercel MCP Server"
}
```

</details>

---

<details>
<summary><code>list_vercel_api_calls</code> - List extracted Vercel API calls</summary>

Returns the full endpoint catalog extracted from Vercel REST API docs.

**Inputs:**

- `category` (string, optional) - Category filter such as `projects`, `deployments`, or `environment`

**Output:**

```json
{
  "count": 274,
  "category": "projects",
  "calls": []
}
```

</details>

---

<details>
<summary><code>list_projects</code> - List projects</summary>

Maps to `GET /v10/projects`.

**Inputs:**

- `auth_token` (string, required) - Vercel bearer token
- `team_id` (string, optional) - Team scope
- `slug` (string, optional) - Team slug scope
- `params` (object, optional) - Query params (`limit`, `search`, etc.)

</details>

---

<details>
<summary><code>get_project</code> - Get a project by ID or name</summary>

Maps to `GET /v9/projects/{idOrName}`.

**Inputs:**

- `auth_token` (string, required)
- `id_or_name` (string, required)
- `team_id` (string, optional)
- `slug` (string, optional)

</details>

---

<details>
<summary><code>create_project</code> - Create a project</summary>

Maps to `POST /v11/projects`.

**Inputs:**

- `auth_token` (string, required)
- `body` (object, required) - Project creation payload
- `team_id` (string, optional)
- `slug` (string, optional)

</details>

---

<details>
<summary><code>update_project</code> - Update a project</summary>

Maps to `PATCH /v9/projects/{idOrName}`.

**Inputs:**

- `auth_token` (string, required)
- `id_or_name` (string, required)
- `body` (object, required)
- `team_id` (string, optional)
- `slug` (string, optional)

</details>

---

<details>
<summary><code>list_deployments</code> - List deployments</summary>

Maps to `GET /v6/deployments`.

**Inputs:**

- `auth_token` (string, required)
- `team_id` (string, optional)
- `slug` (string, optional)
- `params` (object, optional)

</details>

---

<details>
<summary><code>get_deployment</code> - Get deployment details</summary>

Maps to `GET /v13/deployments/{idOrUrl}`.

**Inputs:**

- `auth_token` (string, required)
- `id_or_url` (string, required)
- `team_id` (string, optional)
- `slug` (string, optional)

</details>

---

<details>
<summary><code>create_deployment</code> - Create deployment</summary>

Maps to `POST /v13/deployments`.

**Inputs:**

- `auth_token` (string, required)
- `body` (object, required)
- `team_id` (string, optional)
- `slug` (string, optional)

</details>

---

<details>
<summary><code>cancel_deployment</code> - Cancel deployment</summary>

Maps to `PATCH /v12/deployments/{id}/cancel`.

**Inputs:**

- `auth_token` (string, required)
- `deployment_id` (string, required)
- `team_id` (string, optional)
- `slug` (string, optional)

</details>

---

<details>
<summary><code>get_deployment_events</code> - Retrieve deployment events</summary>

Maps to `GET /v3/deployments/{idOrUrl}/events`.

**Inputs:**

- `auth_token` (string, required)
- `id_or_url` (string, required)
- `team_id` (string, optional)
- `slug` (string, optional)
- `params` (object, optional)

</details>

---

<details>
<summary><code>list_project_environment_variables</code> - List project environment variables</summary>

Maps to `GET /v10/projects/{idOrName}/env`.

**Inputs:**

- `auth_token` (string, required)
- `id_or_name` (string, required)
- `team_id` (string, optional)
- `slug` (string, optional)
- `params` (object, optional)

</details>

---

<details>
<summary><code>create_project_environment_variables</code> - Create project environment variables</summary>

Maps to `POST /v10/projects/{idOrName}/env`.

**Inputs:**

- `auth_token` (string, required)
- `id_or_name` (string, required)
- `body` (object or array, required)
- `team_id` (string, optional)
- `slug` (string, optional)

</details>

---

<details>
<summary><code>update_project_environment_variable</code> - Update a project environment variable</summary>

Maps to `PATCH /v9/projects/{idOrName}/env/{id}`.

**Inputs:**

- `auth_token` (string, required)
- `id_or_name` (string, required)
- `environment_variable_id` (string, required)
- `body` (object, required)
- `team_id` (string, optional)
- `slug` (string, optional)

</details>

---

<details>
<summary><code>list_project_domains</code> - List project domains</summary>

Maps to `GET /v9/projects/{idOrName}/domains`.

**Inputs:**

- `auth_token` (string, required)
- `id_or_name` (string, required)
- `team_id` (string, optional)
- `slug` (string, optional)
- `params` (object, optional)

</details>

---

<details>
<summary><code>add_project_domain</code> - Add domain to project</summary>

Maps to `POST /v10/projects/{idOrName}/domains`.

**Inputs:**

- `auth_token` (string, required)
- `id_or_name` (string, required)
- `body` (object, required)
- `team_id` (string, optional)
- `slug` (string, optional)

</details>

---

<details>
<summary><code>assign_deployment_alias</code> - Assign alias to deployment</summary>

Maps to `POST /v2/deployments/{id}/aliases`.

**Inputs:**

- `auth_token` (string, required)
- `deployment_id` (string, required)
- `body` (object, required)
- `team_id` (string, optional)
- `slug` (string, optional)

</details>

---

<details>
<summary><code>list_deployment_aliases</code> - List deployment aliases</summary>

Maps to `GET /v2/deployments/{id}/aliases`.

**Inputs:**

- `auth_token` (string, required)
- `deployment_id` (string, required)
- `team_id` (string, optional)
- `slug` (string, optional)

</details>

---

<details>
<summary><code>get_runtime_logs_for_deployment</code> - Get deployment runtime logs</summary>

Maps to `GET /v1/projects/{projectId}/deployments/{deploymentId}/runtime-logs`.

**Inputs:**

- `auth_token` (string, required)
- `project_id` (string, required)
- `deployment_id` (string, required)
- `team_id` (string, optional)
- `slug` (string, optional)
- `params` (object, optional)

</details>

---

<details>
<summary><code>vercel_api_request</code> - Generic Vercel endpoint fallback</summary>

Calls any Vercel REST endpoint when a dedicated wrapper tool is not yet available.

**Inputs:**

- `auth_token` (string, required)
- `method` (string, required)
- `path` (string, required)
- `team_id` (string, optional)
- `slug` (string, optional)
- `headers` (object, optional)
- `params` (object, optional)
- `json_body` (any, optional)
- `body` (string, optional)
- `timeout_seconds` (number, optional)
- `follow_redirects` (boolean, optional)
- `max_response_chars` (integer, optional)

**Usage Example:**

```json
{
  "tool": "vercel_api_request",
  "arguments": {
    "auth_token": "<VERCEL_TOKEN>",
    "method": "GET",
    "path": "/v10/projects",
    "team_id": "team_xxx"
  }
}
```

</details>

---

## API Parameters Reference

<details>
<summary><strong>Common Parameters</strong></summary>

- `auth_token` - Vercel bearer token provided per tenant-facing call
- `team_id` - Team context (`teamId` query value)
- `slug` - Team slug context (`slug` query value)
- `params` - Additional endpoint-specific query parameters
- `body` / `json_body` - Endpoint payload for write operations

**Resource Formats**

- Project: `id_or_name` (example: `my-project`)
- Deployment: `deployment_id` or `id_or_url` (example: `dpl_abc123`)
- Environment Variable: `environment_variable_id` (example: `env_abc123`)

</details>

---

## Authentication Guide

<details>
<summary><strong>Vercel API Key Guide</strong></summary>

Tenant-facing tools require authentication via bearer token.

### Step 1: Create Token

1. Open Vercel account token settings: https://vercel.com/account/tokens
2. Create a personal access token
3. Copy and securely store the token

### Step 2: Use Token in Tool Calls

Pass token as `auth_token` in each tenant-facing tool call.

### Step 3: Team Scope

If operating on team resources, include:

- `team_id` and/or
- `slug`

</details>

---

## Setup

```bash
pip install -r requirements.txt
```

## Running the Server

```bash
# stdio
python server.py

# sse
python server.py --transport sse --host 127.0.0.1 --port 8001

# streamable-http
python server.py --transport streamable-http --host 127.0.0.1 --port 8001
```

---

## Troubleshooting

<details>
<summary><strong>Common Issues</strong></summary>

### Missing or Invalid Token

- Cause: Invalid or expired `auth_token`
- Solution: Generate a new token and retry

### Team Resource Access Errors

- Cause: Team-scoped endpoint called without `team_id`/`slug`
- Solution: Add the correct team scope params

### Malformed Request Payload

- Cause: Missing required fields in `body` or invalid types
- Solution: Validate payload shape against Vercel endpoint docs

### Unknown Endpoint Path

- Cause: Wrong API version or path in `vercel_api_request`
- Solution: Use `list_vercel_api_calls` to discover valid method/path pairs

</details>

---

## Resources

<details>
<summary><strong>Links</strong></summary>

- Vercel REST API Docs: https://vercel.com/docs/rest-api
- Vercel Token Management: https://vercel.com/account/tokens
- FastMCP Docs: https://gofastmcp.com/v2/getting-started/welcome
- Local extracted endpoint catalog: `vercel_mcp/vercel_endpoints.json`

</details>

---

## Project Structure

```text
cl-mcp-vercel/
|-- server.py
|-- requirements.txt
|-- README.md
`-- vercel_mcp/
    |-- __init__.py
    |-- cli.py
    |-- config.py
    |-- tools.py
    |-- schemas.py
    |-- service.py
    `-- vercel_endpoints.json
```
