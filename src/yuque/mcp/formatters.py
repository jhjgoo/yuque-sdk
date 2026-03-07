"""Response formatters for MCP protocol.

This module provides formatters for converting Yuque API responses
into human-readable text format with emojis and structured layout.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, cast

from yuque.models import (
    Document,
    Group,
    GroupMember,
    Repository,
    SearchResult,
    TocNode,
    User,
)


def _format_datetime(dt: datetime | None) -> str:
    """Format datetime to readable string.

    Args:
        dt: Datetime object or None.

    Returns:
        Formatted datetime string.
    """
    if dt is None:
        return "N/A"
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def get_public_label(public: int) -> str:
    """Get public level label.

    Args:
        public: Public level code.

    Returns:
        Human-readable public label.
    """
    labels = {
        0: "🔒 私有",
        1: "🌐 公开",
        2: "🏢 企业内部",
    }
    return labels.get(public, f"未知({public})")


# Keep internal version for backward compatibility
_get_public_label = get_public_label


def _get_role_label(role: int) -> str:
    """Get role label for group member.

    Args:
        role: Role code.

    Returns:
        Human-readable role label.
    """
    labels = {
        0: "👑 管理员",
        1: "👤 成员",
        2: "👁️ 只读",
    }
    return labels.get(role, f"未知({role})")


def format_user_info(user: User | dict[str, Any]) -> str:
    """Format user information.

    Args:
        user: User object or dictionary.

    Returns:
        Formatted user information string.
    """
    if isinstance(user, dict):
        user = User(**user)

    lines = [
        "👤 用户信息",
        "=" * 50,
        f"  🆔 ID: {user.id}",
        f"  📛 用户名: {user.login}",
        f"  📖 显示名: {user.name}",
    ]

    if user.avatar_url:
        lines.append(f"  🖼️ 头像: {user.avatar_url}")

    if user.email:
        lines.append(f"  📧 邮箱: {user.email}")

    if user.html_url:
        lines.append(f"  🔗 主页: {user.html_url}")

    lines.extend(
        [
            f"  📅 创建时间: {_format_datetime(user.created_at)}",
            f"  🔄 更新时间: {_format_datetime(user.updated_at)}",
        ]
    )

    return "\n".join(lines)


def format_user_groups(groups: list[Group] | list[dict[str, Any]]) -> str:
    """Format user groups list.

    Args:
        groups: List of Group objects or dictionaries.

    Returns:
        Formatted groups list string.
    """
    if not groups:
        return "👥 团队列表\n" + "=" * 50 + "\n  暂无团队"

    lines = [
        "👥 团队列表",
        "=" * 50,
    ]

    for idx, group in enumerate(groups, 1):
        if isinstance(group, dict):
            group = Group(**group)
        group = cast(Group, group)

        lines.extend(
            [
                f"\n{idx}. {group.name} (@{group.login})",
                f"   🆔 ID: {group.id}",
            ]
        )

        if group.description:
            lines.append(f"   📝 描述: {group.description}")

        lines.extend(
            [
                f"   👥 成员数: {group.members_count}",
                f"   📚 知识库数: {group.books_count}",
            ]
        )

    return "\n".join(lines)


def format_group_info(group: Group | dict[str, Any]) -> str:
    """Format group information.

    Args:
        group: Group object or dictionary.

    Returns:
        Formatted group information string.
    """
    if isinstance(group, dict):
        group = Group(**group)

    lines = [
        "👥 团队信息",
        "=" * 50,
        f"  🆔 ID: {group.id}",
        f"  📛 登录名: {group.login}",
        f"  📖 显示名: {group.name}",
    ]

    if group.description:
        lines.append(f"  📝 描述: {group.description}")

    if group.avatar_url:
        lines.append(f"  🖼️ 头像: {group.avatar_url}")

    lines.extend(
        [
            f"  👑 创建者ID: {group.owner_id}",
            f"  👥 成员数: {group.members_count}",
            f"  📚 知识库数: {group.books_count}",
            f"  📅 创建时间: {_format_datetime(group.created_at)}",
            f"  🔄 更新时间: {_format_datetime(group.updated_at)}",
        ]
    )

    return "\n".join(lines)


def format_group_members(members: list[GroupMember] | list[dict[str, Any]]) -> str:
    """Format group members list.

    Args:
        members: List of GroupMember objects or dictionaries.

    Returns:
        Formatted members list string.
    """
    if not members:
        return "👥 团队成员\n" + "=" * 50 + "\n  暂无成员"

    lines = [
        "👥 团队成员",
        "=" * 50,
    ]

    for idx, member in enumerate(members, 1):
        if isinstance(member, dict):
            member = GroupMember(**member)
        member = cast(GroupMember, member)

        user_info = ""
        if member.user:
            user_info = f" - {member.user.name} (@{member.user.login})"

        lines.extend(
            [
                f"\n{idx}. 用户ID: {member.user_id}{user_info}",
                f"   🎭 角色: {_get_role_label(member.role)}",
                f"   📅 加入时间: {_format_datetime(member.created_at)}",
            ]
        )

    return "\n".join(lines)


def format_repo_info(repo: Repository | dict[str, Any]) -> str:
    """Format repository information.

    Args:
        repo: Repository object or dictionary.

    Returns:
        Formatted repository information string.
    """
    if isinstance(repo, dict):
        repo = Repository(**repo)

    lines = [
        "📚 知识库信息",
        "=" * 50,
        f"  🆔 ID: {repo.id}",
        f"  📛 标识: {repo.slug}",
        f"  📖 名称: {repo.name}",
        f"  📂 类型: {repo.type}",
        f"  🔐 可见性: {_get_public_label(repo.public)}",
    ]

    if repo.description:
        lines.append(f"  📝 描述: {repo.description}")

    if repo.logo:
        lines.append(f"  🖼️ Logo: {repo.logo}")

    lines.extend(
        [
            f"  👤 创建者ID: {repo.creator_id}",
            f"  📑 有目录: {'是' if repo.has_toc else '否'}",
            f"  📅 创建时间: {_format_datetime(repo.created_at)}",
            f"  🔄 更新时间: {_format_datetime(repo.updated_at)}",
        ]
    )

    if repo.user:
        lines.append(f"\n  👤 创建者: {repo.user.name} (@{repo.user.login})")

    if repo.group:
        lines.append(f"  👥 所属团队: {repo.group.name} (@{repo.group.login})")

    return "\n".join(lines)


def format_repo_list(repos: list[Repository] | list[dict[str, Any]]) -> str:
    """Format repository list.

    Args:
        repos: List of Repository objects or dictionaries.

    Returns:
        Formatted repository list string.
    """
    if not repos:
        return "📚 知识库列表\n" + "=" * 50 + "\n  暂无知识库"

    lines = [
        "📚 知识库列表",
        "=" * 50,
    ]

    for idx, repo in enumerate(repos, 1):
        if isinstance(repo, dict):
            repo = Repository(**repo)
        repo = cast(Repository, repo)

        visibility = _get_public_label(repo.public)
        lines.extend(
            [
                f"\n{idx}. {repo.name} ({repo.slug})",
                f"   🆔 ID: {repo.id} | 📂 类型: {repo.type} | {visibility}",
            ]
        )

        if repo.description:
            desc = (
                repo.description[:100] + "..." if len(repo.description) > 100 else repo.description
            )
            lines.append(f"   📝 {desc}")

        owner_info = ""
        if repo.user:
            owner_info = f"👤 {repo.user.name}"
        elif repo.group:
            owner_info = f"👥 {repo.group.name}"

        if owner_info:
            lines.append(f"   {owner_info}")

    return "\n".join(lines)


def format_repo_toc(toc: list[TocNode] | list[dict[str, Any]]) -> str:
    """Format repository table of contents.

    Args:
        toc: List of TocNode objects or dictionaries.

    Returns:
        Formatted TOC string.
    """
    if not toc:
        return "📑 知识库目录\n" + "=" * 50 + "\n  暂无目录"

    def format_node(node: TocNode, indent: str = "") -> list[str]:
        """Recursively format a TOC node and its children."""
        lines = [f"{indent}📄 {node.title} (ID: {node.document_id})"]

        if node.children:
            for child in node.children:
                lines.extend(format_node(child, indent + "  "))

        return lines

    lines = [
        "📑 知识库目录",
        "=" * 50,
    ]

    for node in toc:
        if isinstance(node, dict):
            node = TocNode(**node)
        lines.extend(format_node(node))

    return "\n".join(lines)


def format_doc_info(doc: Document | dict[str, Any]) -> str:
    """Format document information.

    Args:
        doc: Document object or dictionary.

    Returns:
        Formatted document information string.
    """
    if isinstance(doc, dict):
        doc = Document(**doc)

    lines = [
        "📄 文档信息",
        "=" * 50,
        f"  🆔 ID: {doc.id}",
        f"  📛 标识: {doc.slug}",
        f"  📖 标题: {doc.title}",
        f"  🔐 可见性: {_get_public_label(doc.public)}",
    ]

    if doc.cover:
        lines.append(f"  🖼️ 封面: {doc.cover}")

    lines.extend(
        [
            f"  👤 创建者ID: {doc.creator_id}",
            f"  ✍️ 最后编辑者ID: {doc.last_editor_id or doc.user_id}",
            f"  📚 所属知识库ID: {doc.book_id}",
            f"  📊 版本: {doc.version}",
            f"  📝 字数: {doc.word_count or 'N/A'}",
        ]
    )

    lines.extend(
        [
            "",
            "  📈 统计信息:",
            f"     👁️ 阅读数: {doc.read_count}",
            f"     ❤️ 点赞数: {doc.likes_count}",
            f"     💬 评论数: {doc.comments_count}",
            "",
            "  📅 时间信息:",
            f"     创建时间: {_format_datetime(doc.created_at)}",
            f"     更新时间: {_format_datetime(doc.updated_at)}",
            f"     发布时间: {_format_datetime(doc.published_at)}",
        ]
    )

    if doc.first_published_at:
        lines.append(f"     首次发布: {_format_datetime(doc.first_published_at)}")

    if doc.user:
        lines.extend(
            [
                "",
                f"  👤 创建者: {doc.user.name} (@{doc.user.login})",
            ]
        )

    if doc.book:
        lines.append(f"  📚 知识库: {doc.book.name} ({doc.book.slug})")

    return "\n".join(lines)


def format_doc_list(docs: list[Document] | list[dict[str, Any]]) -> str:
    """Format document list.

    Args:
        docs: List of Document objects or dictionaries.

    Returns:
        Formatted document list string.
    """
    if not docs:
        return "📄 文档列表\n" + "=" * 50 + "\n  暂无文档"

    lines = [
        "📄 文档列表",
        "=" * 50,
    ]

    for idx, doc in enumerate(docs, 1):
        if isinstance(doc, dict):
            doc = Document(**doc)
        doc = cast(Document, doc)

        visibility = _get_public_label(doc.public)
        lines.extend(
            [
                f"\n{idx}. {doc.title}",
                f"   🆔 ID: {doc.id} | 📛 Slug: {doc.slug} | {visibility}",
                f"   📊 版本: {doc.version} | 📝 字数: {doc.word_count or 'N/A'}",
                f"   👁️ {doc.read_count} | ❤️ {doc.likes_count} | 💬 {doc.comments_count}",
                f"   📅 更新: {_format_datetime(doc.updated_at)}",
            ]
        )

    return "\n".join(lines)


def format_search_results(results: list[SearchResult] | list[dict[str, Any]]) -> str:
    """Format search results.

    Args:
        results: List of SearchResult objects or dictionaries.

    Returns:
        Formatted search results string.
    """
    if not results:
        return "🔍 搜索结果\n" + "=" * 50 + "\n  未找到相关内容"

    lines = [
        "🔍 搜索结果",
        "=" * 50,
    ]

    type_icons = {
        "doc": "📄",
        "book": "📚",
        "user": "👤",
        "group": "👥",
    }

    for idx, result in enumerate(results, 1):
        if isinstance(result, dict):
            result = SearchResult(**result)
        result = cast(SearchResult, result)

        icon = type_icons.get(result.type, "📌")

        lines.extend(
            [
                f"\n{idx}. {icon} {result.title}",
                f"   📂 类型: {result.type} | 🆔 ID: {result.id}",
            ]
        )

        if result.summary:
            summary = result.summary[:150] + "..." if len(result.summary) > 150 else result.summary
            lines.append(f"   📝 {summary}")

        if result.url:
            lines.append(f"   🔗 {result.url}")

        if result.user:
            lines.append(f"   👤 用户: {result.user.name} (@{result.user.login})")

        if result.book:
            lines.append(f"   📚 知识库: {result.book.name}")

    return "\n".join(lines)


def format_response(data: Any) -> dict[str, Any]:
    """Format Yuque API response for MCP protocol.

    This is a generic formatter that determines the appropriate
    formatting function based on the data type.

    Args:
        data: The data to format (can be model, list, or dict).

    Returns:
        MCP-formatted response dictionary with 'content' key.
    """
    if data is None:
        return {"content": "暂无数据"}

    if isinstance(data, list):
        if not data:
            return {"content": "列表为空"}

        first = data[0]
        if isinstance(first, User):
            return {"content": format_user_groups(data)}
        elif isinstance(first, Group):
            return {"content": format_user_groups(data)}
        elif isinstance(first, GroupMember):
            return {"content": format_group_members(data)}
        elif isinstance(first, Repository):
            return {"content": format_repo_list(data)}
        elif isinstance(first, Document):
            return {"content": format_doc_list(data)}
        elif isinstance(first, SearchResult):
            return {"content": format_search_results(data)}
        elif isinstance(first, TocNode):
            return {"content": format_repo_toc(data)}
        elif isinstance(first, dict):
            if "title" in first and "slug" in first and "book_id" in first:
                return {"content": format_doc_list(data)}
            elif "name" in first and "slug" in first and "type" in first:
                return {"content": format_repo_list(data)}
            elif "login" in first and "members_count" in first:
                return {"content": format_user_groups(data)}

    if isinstance(data, User):
        return {"content": format_user_info(data)}
    elif isinstance(data, Group):
        return {"content": format_group_info(data)}
    elif isinstance(data, Repository):
        return {"content": format_repo_info(data)}
    elif isinstance(data, Document):
        return {"content": format_doc_info(data)}

    if isinstance(data, dict):
        if "title" in data and "slug" in data and "book_id" in data:
            return {"content": format_doc_info(data)}
        elif "name" in data and "slug" in data and "type" in data:
            return {"content": format_repo_info(data)}
        elif "login" in data and "members_count" in data:
            return {"content": format_group_info(data)}
        elif "login" in data and "email" in data:
            return {"content": format_user_info(data)}

    return {"content": str(data)}
