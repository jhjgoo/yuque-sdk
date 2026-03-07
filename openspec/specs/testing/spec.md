# Testing Specification

## Requirements

### Requirement: Test Coverage Threshold
The system SHALL maintain ≥90% code coverage for all modules.

#### Scenario: Coverage Enforcement in CI
- **GIVEN** a pull request with code changes
- **WHEN** CI pipeline runs tests
- **THEN** pytest-cov reports coverage
- **AND** build fails if coverage < 90%

#### Scenario: Coverage Report Generation
- **GIVEN** test suite execution
- **WHEN** tests complete
- **THEN** HTML report is generated in `htmlcov/`
- **AND** XML report is generated for CI tools
- **AND** terminal report shows missing lines

### Requirement: Test Organization
The system SHALL mirror source structure in test directory.

#### Scenario: Test File Naming
- **GIVEN** a source file `src/yuque/api/user.py`
- **WHEN** writing tests
- **THEN** test file is at `tests/test_user.py`
- **AND** test class is `TestUserAPI`

#### Scenario: MCP Tool Tests
- **GIVEN** an MCP tool `src/yuque/mcp/tools/doc.py`
- **WHEN** writing tests
- **THEN** test file is at `tests/mcp/tools/test_doc.py`
- **AND** all tool functions are tested

### Requirement: Test Patterns
The system SHALL use pytest fixtures and mocking appropriately.

#### Scenario: Client Fixture Usage
- **GIVEN** multiple tests need client
- **WHEN** using `@pytest.fixture`
- **THEN** client is created once per test session
- **AND** credentials are loaded from config.yaml

#### Scenario: API Mocking
- **GIVEN** unit tests for API methods
- **WHEN** testing error handling
- **THEN** httpx client is mocked
- **AND** no real HTTP calls are made

### Requirement: Async Test Support
The system SHALL support async test functions.

#### Scenario: Async Test Function
- **GIVEN** an async API method
- **WHEN** writing tests
- **THEN** test function is `async def test_...`
- **AND** pytest-asyncio handles execution

#### Scenario: Async Context Manager Test
- **GIVEN** async context manager usage
- **WHEN** testing resource cleanup
- **THEN** `async with` is used in test
- **AND** cleanup is verified with mocks
