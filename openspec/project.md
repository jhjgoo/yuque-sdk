# Yuque Python SDK Project

## Tech Stack
- **Language**: Python 3.10+ with type hints
- **HTTP Client**: httpx (async + sync)
- **Data Validation**: Pydantic v2
- **Configuration**: pydantic-settings
- **Package Manager**: uv
- **Testing**: pytest, pytest-asyncio, pytest-cov
- **Code Quality**: ruff, mypy (strict mode)

## Architecture

### Layered Architecture
```
src/yuque/
├── api/          # API layer - HTTP client wrappers
├── models/       # Data models - Pydantic schemas
├── exceptions/   # Exception hierarchy
├── cache/        # Caching layer (memory + Redis)
├── mcp/          # MCP server implementation
├── utils/        # Utility functions
└── client.py     # Main client facade
```

### Key Patterns

1. **Dual Access Pattern**
   - Access resources by ID: `client.doc.get(doc_id=123)`
   - Access resources by path: `client.doc.get_by_path("group/book/slug")`

2. **Async/Sync Support**
   - All API methods have sync and async variants
   - Async methods have `_async` suffix
   - Context managers for resource management

3. **Error Handling**
   - Custom exception hierarchy in `exceptions/__init__.py`
   - HTTP status codes mapped to specific exceptions
   - All exceptions include request context

4. **Caching Strategy**
   - Memory backend (default): LRU cache with TTL
   - Redis backend (optional): Distributed caching
   - Automatic TTL policies based on endpoint type
   - Cache invalidation on mutations

5. **MCP Server Architecture**
   - FastMCP framework for MCP protocol
   - 27 tools exposing Yuque API functionality
   - STDIO transport (default), SSE/HTTP optional
   - Tool registration via decorator pattern

## Code Standards

### Naming Conventions
- **Files**: `snake_case.py`
- **Classes**: `PascalCase`
- **Functions/Methods**: `snake_case`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private members**: `_leading_underscore`

### Type Hints
- Required on all public APIs
- Use `|` union syntax (Python 3.10+)
- Use `TYPE_CHECKING` for circular import avoidance
- Prefer `dict[str, Any]` over `Dict[str, Any]`

### Documentation
- Docstrings only for public APIs
- Use Google-style docstring format
- Include usage examples in docstrings
- Keep docstrings concise and actionable

### Error Handling
- Never use bare `except:`
- Catch specific exception types
- Include context in error messages
- Use custom exceptions from `yuque.exceptions`

### Testing
- 90%+ code coverage required
- Use pytest fixtures for test setup
- Mock external API calls in unit tests
- Integration tests use real API (staging)

## Dependencies

### Core Dependencies
- `httpx>=0.27.0` - HTTP client
- `pydantic>=2.0.0` - Data validation
- `pydantic-settings>=2.0.0` - Configuration

### Optional Dependencies
- `mcp>=0.9.0` - MCP server support
- `fastapi>=0.100.0` - HTTP transport
- `uvicorn>=0.22.0` - ASGI server
- `redis>=5.0.0` - Redis caching

### Development Dependencies
- `pytest>=8.0.0` - Testing framework
- `pytest-asyncio>=0.23.0` - Async test support
- `pytest-cov>=4.1.0` - Coverage reporting
- `ruff>=0.4.0` - Linting and formatting
- `mypy>=1.8.0` - Type checking

## Project Structure

### Source Code
- `src/yuque/` - Main package
- `tests/` - Test suite (mirror src structure)
- `examples/` - Usage examples
- `docs/` - Documentation

### Configuration Files
- `pyproject.toml` - Project configuration
- `config.yaml` - Test credentials (gitignored)
- `.gitignore` - Git ignore rules
- `.env` - Environment variables (gitignored)

## Development Workflow

### Setup
```bash
# Clone repository
git clone <repo-url>
cd yuque-python

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
uv pip install -e ".[dev,mcp]"

# Configure test credentials
cp config.example.yaml config.yaml
# Edit config.yaml with your Yuque API token
```

### Running Tests
```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src/yuque --cov-report=html

# Run specific test file
pytest tests/test_client.py -v
```

### Code Quality
```bash
# Format code
ruff format src/ tests/

# Lint code
ruff check src/ tests/

# Type check
mypy src/yuque
```

### Publishing
```bash
# Set PyPI token
export PYPI_TOKEN="your-token"

# Build and publish
./build.sh
```

## Security

### API Token Management
- **NEVER** hardcode tokens in source code
- Use environment variables: `YUQUE_TOKEN`
- Use `config.yaml` for tests (gitignored)
- Revoke tokens immediately if exposed

### Input Validation
- All external inputs validated via Pydantic
- Type checking enforced at runtime
- SQL injection prevention via parameterized queries (future DB support)

### Error Messages
- Sanitize error messages before logging
- Never expose API tokens in logs
- Include request IDs for debugging
- Use structured logging (JSON format)

## Performance

### Caching
- Default TTL: 3 hours for documents
- Repository list: 12 hours
- User info: 24 hours
- Search results: 1 hour

### Connection Pooling
- Reuse HTTP connections via httpx
- Configurable pool size
- Automatic retry with backoff

### Rate Limiting
- Respect Yuque API rate limits
- Implement exponential backoff
- Cache frequently accessed data

## Monitoring

### Logging
- Structured JSON logging
- Log to stderr (for MCP servers)
- Configurable log levels
- Include request/response IDs

### Metrics (Future)
- Request latency tracking
- Cache hit/miss rates
- Error rate monitoring
- API call frequency

## Maintenance

### Dependency Updates
- Monthly security updates
- Quarterly feature updates
- Use Dependabot for automation

### Code Quality Gates
- All tests must pass
- Coverage must be ≥90%
- No linting errors
- Type checking must pass
- No security vulnerabilities

### Release Process
1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Run full test suite
4. Build package: `python -m build`
5. Upload to PyPI: `./build.sh`
6. Create GitHub release
