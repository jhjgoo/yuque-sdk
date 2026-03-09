"""Search-related MCP tools for Yuque API.

This module provides MCP tools for search operations:
- Search across Yuque content (documents, repositories, users, groups)
"""

from mcp.server.fastmcp import FastMCP

from ...client import YuqueClient

from ..adapters import adapt_error


async def search_content(
    client: YuqueClient,
    keyword: str,
    type: str = "doc",
    page: int = 1,
) -> str:
    """Search across Yuque content.

    This tool searches for content across Yuque, including documents, repositories,
    users, and groups. Results are returned in a paginated format.

    Args:
        client: Authenticated YuqueClient instance.
        keyword: Search keyword or phrase.
        type: Type of content to search for. Options:
            - "doc": Search documents (default)
            - "book": Search repositories/knowledge bases
            - "user": Search users
            - "group": Search groups/teams
        page: Page number for pagination (default: 1).

    Returns:
        Formatted search results including:
        - Total number of results
        - Result details (title, summary, URL, etc.)
        - Pagination information

    Example:
        ```python
        # Search for documents
        results = await search_content(client, keyword="python", type="doc")
        print(results)

        # Search for repositories
        results = await search_content(client, keyword="api", type="book", page=2)
        print(results)
        ```
    """
    try:
        valid_types = {"doc", "book", "user", "group"}
        if type not in valid_types:
            return f"Invalid type '{type}'. Must be one of: {', '.join(sorted(valid_types))}"

        response = await client.search.search_async(
            keyword=keyword,
            type=type,
            page=page,
        )

        results = response.data if response.data else []
        meta = response.meta

        lines = [
            f"# Search Results for '{keyword}'",
            "",
            f"**Type**: {type}",
            f"**Page**: {page}",
        ]

        if meta:
            lines.append(f"**Total Results**: {meta.total}")
            lines.append(f"**Total Pages**: {meta.total_pages}")
            lines.append(f"**Results Per Page**: {meta.per_page}")

        lines.append("")

        if not results:
            lines.append("No results found.")
            lines.append("")
            lines.append("💡 **Tips**:")
            lines.append("- Try different keywords")
            lines.append("- Check for typos")
            lines.append("- Use broader search terms")
            return "\n".join(lines)

        lines.append(f"Found {len(results)} result(s) on this page:")
        lines.append("")

        for idx, result in enumerate(results, 1):
            if isinstance(result, dict):
                result_id = result.get("id", "N/A")
                result_type = result.get("type", type)
                title = result.get("title", "Untitled")
                summary = result.get("summary")
                url = result.get("url")
                user = result.get("user")
                book = result.get("book")
            else:
                result_id = getattr(result, "id", "N/A")
                result_type = getattr(result, "type", type)
                title = getattr(result, "title", "Untitled")
                summary = getattr(result, "summary", None)
                url = getattr(result, "url", None)
                user = getattr(result, "user", None)
                book = getattr(result, "book", None)

            lines.append(f"## {idx}. {title}")
            lines.append(f"- **ID**: {result_id}")
            lines.append(f"- **Type**: {result_type}")

            if summary:
                max_summary_len = 200
                display_summary = (
                    summary[:max_summary_len] + "..." if len(summary) > max_summary_len else summary
                )
                lines.append(f"- **Summary**: {display_summary}")

            if url:
                lines.append(f"- **URL**: {url}")

            if user:
                if isinstance(user, dict):
                    user_name = user.get("name")
                    user_login = user.get("login")
                else:
                    user_name = getattr(user, "name", None)
                    user_login = getattr(user, "login", None)
                if user_name or user_login:
                    lines.append(f"- **Author**: {user_name or user_login}")

            if book:
                if isinstance(book, dict):
                    book_name = book.get("name")
                    book_slug = book.get("slug")
                else:
                    book_name = getattr(book, "name", None)
                    book_slug = getattr(book, "slug", None)
                if book_name or book_slug:
                    lines.append(f"- **Repository**: {book_name or book_slug}")

            lines.append("")

        if meta and meta.total_pages > 1:
            lines.append("---")
            lines.append("")
            lines.append("📄 **Pagination**:")
            if page > 1:
                lines.append(f"- Previous page: Use `page={page - 1}`")
            if page < meta.total_pages:
                lines.append(f"- Next page: Use `page={page + 1}`")

        return "\n".join(lines)

    except Exception as e:
        error_response = adapt_error(e)
        return f"Error searching for '{keyword}': {error_response['error']['message']}"


def register_search_tools(mcp: FastMCP, client: YuqueClient) -> None:
    """Register all search-related MCP tools with the server.

    This function registers the following tools:
    - yuque_search: Search across Yuque content

    Args:
        mcp: The FastMCP server instance to register tools with.
        client: Authenticated YuqueClient instance.

    Example:
        ```python
        from mcp.server.fastmcp import FastMCP
        from yuque import YuqueClient
        from yuque.mcp.tools.search import register_search_tools

        mcp = FastMCP("yuque-mcp")
        client = YuqueClient(token="your-token")
        register_search_tools(mcp, client)
        ```
    """

    @mcp.tool()
    async def yuque_search(
        keyword: str,
        type: str = "doc",
        page: int = 1,
    ) -> str:
        """Search across Yuque content including documents, repositories, users, and groups.

        This tool performs a full-text search across Yuque's content database.
        You can search for specific types of content or search across all types.

        Args:
            keyword: The search keyword or phrase. Can be a single word or multiple words.
            type: Type of content to search for. Valid options:
                - "doc": Search for documents (default)
                - "book": Search for repositories/knowledge bases
                - "user": Search for users
                - "group": Search for groups/teams
            page: Page number for paginating through results (default: 1).
                  Each page typically contains 20 results.

        Returns:
            Formatted search results as markdown text, including:
            - Total number of matching results
            - Result details (title, summary, URL, author, etc.)
            - Pagination information and navigation hints

        Examples:
            Search for documents about Python:
            ```python
            yuque_search(keyword="python", type="doc")
            ```

            Search for repositories:
            ```python
            yuque_search(keyword="api documentation", type="book")
            ```

            Search for users:
            ```python
            yuque_search(keyword="john", type="user")
            ```

            Get second page of results:
            ```python
            yuque_search(keyword="tutorial", type="doc", page=2)
            ```
        """
        return await search_content(client, keyword, type, page)
