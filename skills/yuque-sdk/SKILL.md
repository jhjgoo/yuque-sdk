---
name: yuque-sdk
description: Development skill for yuque-python-sdk library. Use when working on the yuque SDK - adding new API endpoints, fixing bugs, writing tests, or extending functionality.
---

# Yuque SDK Development Guide

When working on the yuque-python-sdk library, follow these patterns:

## Project Structure

```
yuque-python-sdk/
├── src/yuque/
│   ├── api/           # API implementations (doc.py, repo.py, user.py, etc.)
│   ├── models/        # Data models
│   ├── client.py     # Main client
│   └── mcp/          # MCP server tools
│       └── tools/     # MCP tool definitions
├── tests/
│   ├── api/          # API unit tests
│   └── mcp/          # MCP tool tests
└── doc/              # OpenAPI specifications
```

## Adding New API Endpoints

1. **Find the API spec** in `doc/yuque_openapi_*.yaml`
2. **Add method to appropriate API class** in `src/yuque/api/`
3. **Register MCP tool** in `src/yuque/mcp/tools/`
4. **Add unit tests** in `tests/api/`

### API Class Pattern

```python
# src/yuque/api/doc.py example
class DocAPI(BaseAPI):
    def get(self, doc_id: int) -> dict[str, Any]:
        response = self._request("GET", f"/api/v2/docs/{doc_id}")
        return response["data"]
```

### MCP Tool Pattern

```python
# src/yuque/mcp/tools/doc.py example
@mcp.tool()
async def yuque_get_doc(doc_id: int) -> dict[str, Any]:
    try:
        doc = client.doc.get(doc_id=doc_id)
        return {"success": True, "data": _format_doc(doc)}
    except Exception as e:
        return {"success": False, "error": str(e)}
```

## Running Tests

```bash
# Create virtual environment
uv venv .venv
source .venv/bin/activate
uv pip install -e ".[all]"

# Run tests (bypass config)
python -m pytest tests/api/ -v -c /dev/null
```

## Common API Paths

- `/api/v2/user` - Current user info
- `/api/v2/users/{login}/repos` - User's repositories
- `/api/v2/repos/{book_id}/docs` - Documents in repo
- `/api/v2/repos/{book_id}/docs/{doc_id}` - Single document
- `/api/v2/groups/{login}/users` - Group members

## Important Notes

- Yuque API requires `book_id` for update/delete operations
- User API doesn't support get by ID - use get_me() instead
- Some endpoints return 404 if not available for your account type
