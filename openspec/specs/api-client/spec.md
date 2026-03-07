# API Client Specification

## Requirements

### Requirement: HTTP Client Architecture
The system SHALL use httpx.AsyncClient for all HTTP operations.

#### Scenario: Connection Pooling
- **GIVEN** multiple concurrent API requests
- **WHEN** the client makes requests
- **THEN** connections are reused from a connection pool
- **AND** pool size is configurable

#### Scenario: Timeout Handling
- **GIVEN** a slow API response
- **WHEN** request exceeds timeout threshold
- **THEN** TimeoutError is raised
- **AND** timeout value is configurable (default 30s)

### Requirement: Dual Access Pattern
The system SHALL support accessing resources by ID or path.

#### Scenario: Access Document by ID
- **GIVEN** a valid document ID
- **WHEN** client.doc.get(doc_id=123) is called
- **THEN** document is retrieved via `/docs/123`
- **AND** Document model is returned

#### Scenario: Access Document by Path
- **GIVEN** a valid group/book/slug path
- **WHEN** client.doc.get_by_path("group/book/slug") is called
- **THEN** document is retrieved via path lookup
- **AND** Document model is returned

### Requirement: Error Handling
The system SHALL map HTTP errors to Python exceptions.

#### Scenario: Authentication Error
- **GIVEN** API returns HTTP 401
- **WHEN** response is received
- **THEN** AuthenticationError is raised
- **AND** error includes request details

#### Scenario: Rate Limit Error
- **GIVEN** API returns HTTP 429
- **WHEN** response is received
- **THEN** RateLimitError is raised
- **AND** error includes retry-after header value

### Requirement: Async/Sync Support
The system SHALL provide both sync and async interfaces.

#### Scenario: Async Document Retrieval
- **GIVEN** an async context
- **WHEN** await client.doc.get_async(doc_id=123) is called
- **THEN** document is retrieved asynchronously
- **AND** AsyncClient is used internally

#### Scenario: Context Manager Usage
- **GIVEN** resource cleanup is needed
- **WHEN** using `async with YuqueClient() as client:`
- **THEN** connections are properly closed on exit
- **AND** no resource leaks occur
