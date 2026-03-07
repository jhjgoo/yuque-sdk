"""Comprehensive tests for MCP response formatters.

Tests all formatter functions with:
- Pydantic model inputs
- Dict inputs
- Optional fields handling
- Edge cases (empty lists, None values)
- Recursive formatting
- String truncation
"""

from __future__ import annotations

from datetime import datetime

import pytest

from yuque.mcp.formatters import (
    format_doc_info,
    format_doc_list,
    format_group_info,
    format_group_members,
    format_repo_info,
    format_repo_list,
    format_repo_toc,
    format_response,
    format_search_results,
    format_user_groups,
    format_user_info,
)
from yuque.models import (
    Document,
    Group,
    GroupMember,
    Repository,
    SearchResult,
    TocNode,
    User,
)


# =============================================================================
# FIXTURES - Sample Data
# =============================================================================


@pytest.fixture
def sample_user() -> User:
    """Create sample user with all fields."""
    return User(
        id=1,
        login="testuser",
        name="Test User",
        avatar_url="https://example.com/avatar.png",
        email="test@example.com",
        html_url="https://yuque.com/testuser",
        created_at=datetime(2024, 1, 15, 10, 30, 0),
        updated_at=datetime(2024, 6, 20, 14, 45, 0),
    )


@pytest.fixture
def sample_user_minimal() -> User:
    """Create sample user with only required fields."""
    return User(
        id=2,
        login="minimal",
        name="Minimal User",
    )


@pytest.fixture
def sample_user_dict() -> dict:
    """Create sample user as dict."""
    return {
        "id": 3,
        "login": "dictuser",
        "name": "Dict User",
        "avatar_url": "https://example.com/dict-avatar.png",
        "email": "dict@example.com",
        "html_url": "https://yuque.com/dictuser",
        "created_at": datetime(2024, 2, 1, 8, 0, 0),
        "updated_at": datetime(2024, 7, 1, 16, 30, 0),
    }


@pytest.fixture
def sample_group() -> Group:
    """Create sample group with all fields."""
    return Group(
        id=100,
        login="testgroup",
        name="Test Group",
        description="A test group for testing",
        avatar_url="https://example.com/group-avatar.png",
        owner_id=1,
        created_at=datetime(2024, 1, 1, 0, 0, 0),
        updated_at=datetime(2024, 6, 1, 12, 0, 0),
        members_count=10,
        books_count=5,
    )


@pytest.fixture
def sample_group_minimal() -> Group:
    """Create sample group with minimal fields."""
    return Group(
        id=101,
        login="minimalgroup",
        name="Minimal Group",
        owner_id=2,
        members_count=0,
        books_count=0,
    )


@pytest.fixture
def sample_group_dict() -> dict:
    """Create sample group as dict."""
    return {
        "id": 102,
        "login": "dictgroup",
        "name": "Dict Group",
        "description": "Group from dict",
        "owner_id": 3,
        "members_count": 3,
        "books_count": 2,
    }


@pytest.fixture
def sample_group_member(sample_user: User) -> GroupMember:
    """Create sample group member with user details."""
    return GroupMember(
        id=1000,
        group_id=100,
        user_id=1,
        role=0,  # Admin
        created_at=datetime(2024, 1, 10, 9, 0, 0),
        user=sample_user,
    )


@pytest.fixture
def sample_group_member_minimal() -> GroupMember:
    """Create sample group member without user details."""
    return GroupMember(
        id=1001,
        group_id=100,
        user_id=2,
        role=1,  # Member
        created_at=datetime(2024, 2, 15, 11, 30, 0),
        user=None,
    )


@pytest.fixture
def sample_repo(sample_user: User, sample_group: Group) -> Repository:
    """Create sample repository with all fields."""
    return Repository(
        id=500,
        type="Book",
        slug="test-repo",
        name="Test Repository",
        description="A test repository",
        creator_id=1,
        public=0,  # Private
        has_toc=True,
        logo="https://example.com/repo-logo.png",
        created_at=datetime(2024, 3, 1, 10, 0, 0),
        updated_at=datetime(2024, 6, 15, 16, 0, 0),
        user=sample_user,
        group=sample_group,
    )


@pytest.fixture
def sample_repo_minimal() -> Repository:
    """Create sample repository with minimal fields."""
    return Repository(
        id=501,
        type="Book",
        slug="minimal-repo",
        name="Minimal Repository",
        creator_id=2,
        public=1,  # Public
        has_toc=False,
    )


@pytest.fixture
def sample_repo_long_desc() -> Repository:
    """Create repository with long description for truncation test."""
    return Repository(
        id=502,
        type="Book",
        slug="long-desc-repo",
        name="Repository with Long Description",
        description="This is a very long description that exceeds the 100 character limit and should be truncated when displayed in the repository list view. The truncation should add ellipsis at the end.",
        creator_id=1,
        public=0,
    )


@pytest.fixture
def sample_doc(sample_user: User, sample_repo: Repository) -> Document:
    """Create sample document with all fields."""
    return Document(
        id=2000,
        slug="test-doc",
        title="Test Document",
        body="# Test Content",
        body_format=1,  # Markdown
        creator_id=1,
        user_id=1,
        book_id=500,
        public=0,
        read_count=100,
        likes_count=25,
        comments_count=10,
        version=5,
        created_at=datetime(2024, 4, 1, 8, 0, 0),
        updated_at=datetime(2024, 6, 20, 14, 30, 0),
        published_at=datetime(2024, 4, 2, 10, 0, 0),
        first_published_at=datetime(2024, 4, 2, 10, 0, 0),
        last_editor_id=1,
        word_count=1500,
        cover="https://example.com/cover.png",
        user=sample_user,
        book=sample_repo,
    )


@pytest.fixture
def sample_doc_minimal() -> Document:
    """Create sample document with minimal fields."""
    return Document(
        id=2001,
        slug="minimal-doc",
        title="Minimal Document",
        body_format=1,
        creator_id=2,
        user_id=2,
        book_id=501,
        public=1,
        version=1,
    )


@pytest.fixture
def sample_toc_node() -> TocNode:
    """Create sample TOC node with children (nested structure)."""
    child1 = TocNode(
        title="Child Document 1",
        slug="child-1",
        document_id=3001,
        parent_id=3000,
        depth=2,
        order=1,
    )
    child2 = TocNode(
        title="Child Document 2",
        slug="child-2",
        document_id=3002,
        parent_id=3000,
        depth=2,
        order=2,
        children=[
            TocNode(
                title="Grandchild Document",
                slug="grandchild",
                document_id=3003,
                parent_id=3002,
                depth=3,
                order=1,
            )
        ],
    )
    return TocNode(
        title="Root Document",
        slug="root",
        document_id=3000,
        parent_id=None,
        depth=1,
        order=1,
        children=[child1, child2],
    )


@pytest.fixture
def sample_search_result(sample_user: User, sample_repo: Repository) -> SearchResult:
    """Create sample search result with all fields."""
    return SearchResult(
        id=4000,
        type="doc",
        title="Search Result Document",
        summary="This is a summary of the search result that might be quite long and should be truncated when displayed in the search results list if it exceeds 150 characters limit.",
        url="https://yuque.com/testgroup/test-repo/test-doc",
        user=sample_user,
        book=sample_repo,
    )


@pytest.fixture
def sample_search_result_minimal() -> SearchResult:
    """Create minimal search result."""
    return SearchResult(
        id=4001,
        type="book",
        title="Minimal Search Result",
    )


# =============================================================================
# TESTS: Helper Functions (via public formatters)
# =============================================================================


class TestHelperFunctions:
    """Tests for internal helper functions via public interfaces."""

    def test_public_label_private(self):
        """Test public label for private (0)."""
        repo = Repository(id=1, type="Book", slug="test", name="Test", creator_id=1, public=0)
        result = format_repo_info(repo)
        assert "🔒 私有" in result

    def test_public_label_public(self):
        """Test public label for public (1)."""
        repo = Repository(id=1, type="Book", slug="test", name="Test", creator_id=1, public=1)
        result = format_repo_info(repo)
        assert "🌐 公开" in result

    def test_public_label_enterprise(self):
        """Test public label for enterprise (2)."""
        repo = Repository(id=1, type="Book", slug="test", name="Test", creator_id=1, public=2)
        result = format_repo_info(repo)
        assert "🏢 企业内部" in result

    def test_public_label_unknown(self):
        """Test public label for unknown value."""
        repo = Repository(id=1, type="Book", slug="test", name="Test", creator_id=1, public=99)
        result = format_repo_info(repo)
        assert "未知(99)" in result

    def test_role_label_admin(self):
        """Test role label for admin (0)."""
        member = GroupMember(id=1, group_id=1, user_id=1, role=0)
        result = format_group_members([member])
        assert "👑 管理员" in result

    def test_role_label_member(self):
        """Test role label for member (1)."""
        member = GroupMember(id=1, group_id=1, user_id=1, role=1)
        result = format_group_members([member])
        assert "👤 成员" in result

    def test_role_label_readonly(self):
        """Test role label for read-only (2)."""
        member = GroupMember(id=1, group_id=1, user_id=1, role=2)
        result = format_group_members([member])
        assert "👁️ 只读" in result

    def test_role_label_unknown(self):
        """Test role label for unknown value."""
        member = GroupMember(id=1, group_id=1, user_id=1, role=99)
        result = format_group_members([member])
        assert "未知(99)" in result

    def test_datetime_format_with_value(self):
        """Test datetime formatting with value."""
        user = User(
            id=1,
            login="test",
            name="Test",
            created_at=datetime(2024, 1, 15, 10, 30, 45),
        )
        result = format_user_info(user)
        assert "2024-01-15 10:30:45" in result

    def test_datetime_format_none(self):
        """Test datetime formatting with None."""
        user = User(id=1, login="test", name="Test", created_at=None)
        result = format_user_info(user)
        assert "N/A" in result


# =============================================================================
# TESTS: format_user_info
# =============================================================================


class TestFormatUserInfo:
    """Tests for format_user_info function."""

    def test_with_full_user_model(self, sample_user: User):
        """Test formatting user with all fields."""
        result = format_user_info(sample_user)

        assert "👤 用户信息" in result
        assert "🆔 ID: 1" in result
        assert "📛 用户名: testuser" in result
        assert "📖 显示名: Test User" in result
        assert "🖼️ 头像: https://example.com/avatar.png" in result
        assert "📧 邮箱: test@example.com" in result
        assert "🔗 主页: https://yuque.com/testuser" in result
        assert "📅 创建时间: 2024-01-15 10:30:00" in result
        assert "🔄 更新时间: 2024-06-20 14:45:00" in result

    def test_with_minimal_user_model(self, sample_user_minimal: User):
        """Test formatting user with only required fields."""
        result = format_user_info(sample_user_minimal)

        assert "🆔 ID: 2" in result
        assert "📛 用户名: minimal" in result
        assert "📖 显示名: Minimal User" in result
        assert "🖼️ 头像" not in result  # Optional, should not appear
        assert "📧 邮箱" not in result  # Optional, should not appear
        assert "🔗 主页" not in result  # Optional, should not appear

    def test_with_dict_input(self, sample_user_dict: dict):
        """Test formatting user from dict input."""
        result = format_user_info(sample_user_dict)

        assert "🆔 ID: 3" in result
        assert "📛 用户名: dictuser" in result
        assert "📖 显示名: Dict User" in result
        assert "🖼️ 头像: https://example.com/dict-avatar.png" in result
        assert "📧 邮箱: dict@example.com" in result


# =============================================================================
# TESTS: format_user_groups
# =============================================================================


class TestFormatUserGroups:
    """Tests for format_user_groups function."""

    def test_with_empty_list(self):
        """Test formatting empty groups list."""
        result = format_user_groups([])
        assert "👥 团队列表" in result
        assert "暂无团队" in result

    def test_with_single_group(self, sample_group: Group):
        """Test formatting single group."""
        result = format_user_groups([sample_group])

        assert "1. Test Group (@testgroup)" in result
        assert "🆔 ID: 100" in result
        assert "📝 描述: A test group for testing" in result
        assert "👥 成员数: 10" in result
        assert "📚 知识库数: 5" in result

    def test_with_multiple_groups(self, sample_group: Group, sample_group_minimal: Group):
        """Test formatting multiple groups."""
        result = format_user_groups([sample_group, sample_group_minimal])

        assert "1. Test Group (@testgroup)" in result
        assert "2. Minimal Group (@minimalgroup)" in result
        assert "👥 成员数: 0" in result

    def test_with_dict_list(self, sample_group_dict: dict):
        """Test formatting groups from dict list."""
        result = format_user_groups([sample_group_dict])

        assert "1. Dict Group (@dictgroup)" in result
        assert "📝 描述: Group from dict" in result

    def test_with_minimal_group_no_description(self, sample_group_minimal: Group):
        """Test that description line is omitted when None."""
        result = format_user_groups([sample_group_minimal])

        assert "📝 描述:" not in result


# =============================================================================
# TESTS: format_group_info
# =============================================================================


class TestFormatGroupInfo:
    """Tests for format_group_info function."""

    def test_with_full_group_model(self, sample_group: Group):
        """Test formatting group with all fields."""
        result = format_group_info(sample_group)

        assert "👥 团队信息" in result
        assert "🆔 ID: 100" in result
        assert "📛 登录名: testgroup" in result
        assert "📖 显示名: Test Group" in result
        assert "📝 描述: A test group for testing" in result
        assert "🖼️ 头像: https://example.com/group-avatar.png" in result
        assert "👑 创建者ID: 1" in result
        assert "👥 成员数: 10" in result
        assert "📚 知识库数: 5" in result

    def test_with_minimal_group_model(self, sample_group_minimal: Group):
        """Test formatting group without optional fields."""
        result = format_group_info(sample_group_minimal)

        assert "🆔 ID: 101" in result
        assert "📝 描述" not in result
        assert "🖼️ 头像" not in result

    def test_with_dict_input(self, sample_group_dict: dict):
        """Test formatting group from dict."""
        result = format_group_info(sample_group_dict)

        assert "🆔 ID: 102" in result
        assert "📛 登录名: dictgroup" in result


# =============================================================================
# TESTS: format_group_members
# =============================================================================


class TestFormatGroupMembers:
    """Tests for format_group_members function."""

    def test_with_empty_list(self):
        """Test formatting empty members list."""
        result = format_group_members([])
        assert "👥 团队成员" in result
        assert "暂无成员" in result

    def test_with_user_details(self, sample_group_member: GroupMember):
        """Test formatting member with user details."""
        result = format_group_members([sample_group_member])

        assert "1. 用户ID: 1 - Test User (@testuser)" in result
        assert "🎭 角色: 👑 管理员" in result

    def test_without_user_details(self, sample_group_member_minimal: GroupMember):
        """Test formatting member without user details."""
        result = format_group_members([sample_group_member_minimal])

        assert "1. 用户ID: 2" in result
        assert "- " not in result.split("用户ID: 2")[1].split("\n")[0]  # No user info appended

    def test_with_multiple_members(
        self, sample_group_member: GroupMember, sample_group_member_minimal: GroupMember
    ):
        """Test formatting multiple members."""
        result = format_group_members([sample_group_member, sample_group_member_minimal])

        assert "1. 用户ID: 1" in result
        assert "2. 用户ID: 2" in result

    def test_with_dict_input(self):
        """Test formatting members from dict list."""
        member_dict = {
            "id": 2000,
            "group_id": 100,
            "user_id": 99,
            "role": 1,
            "created_at": datetime(2024, 5, 1, 12, 0, 0),
            "user": None,
        }
        result = format_group_members([member_dict])

        assert "用户ID: 99" in result


# =============================================================================
# TESTS: format_repo_info
# =============================================================================


class TestFormatRepoInfo:
    """Tests for format_repo_info function."""

    def test_with_full_repo_model(self, sample_repo: Repository):
        """Test formatting repository with all fields."""
        result = format_repo_info(sample_repo)

        assert "📚 知识库信息" in result
        assert "🆔 ID: 500" in result
        assert "📛 标识: test-repo" in result
        assert "📖 名称: Test Repository" in result
        assert "📂 类型: Book" in result
        assert "🔐 可见性: 🔒 私有" in result
        assert "📝 描述: A test repository" in result
        assert "🖼️ Logo: https://example.com/repo-logo.png" in result
        assert "👤 创建者ID: 1" in result
        assert "📑 有目录: 是" in result
        assert "👤 创建者: Test User (@testuser)" in result
        assert "👥 所属团队: Test Group (@testgroup)" in result

    def test_with_minimal_repo_model(self, sample_repo_minimal: Repository):
        """Test formatting repository without optional fields."""
        result = format_repo_info(sample_repo_minimal)

        assert "🆔 ID: 501" in result
        assert "📝 描述" not in result
        assert "🖼️ Logo" not in result
        assert "📑 有目录: 否" in result
        assert "🔐 可见性: 🌐 公开" in result

    def test_with_dict_input(self):
        """Test formatting repository from dict."""
        repo_dict = {
            "id": 600,
            "type": "Book",
            "slug": "dict-repo",
            "name": "Dict Repository",
            "creator_id": 1,
            "public": 2,
        }
        result = format_repo_info(repo_dict)

        assert "🆔 ID: 600" in result
        assert "🔐 可见性: 🏢 企业内部" in result

    def test_with_only_user_owner(self, sample_user: User):
        """Test repository owned by user (not group)."""
        repo = Repository(
            id=700,
            type="Book",
            slug="user-repo",
            name="User Repository",
            creator_id=1,
            public=0,
            user=sample_user,
            group=None,
        )
        result = format_repo_info(repo)

        assert "👤 创建者: Test User (@testuser)" in result
        assert "👥 所属团队" not in result

    def test_with_only_group_owner(self, sample_group: Group):
        """Test repository owned by group (no user)."""
        repo = Repository(
            id=800,
            type="Book",
            slug="group-repo",
            name="Group Repository",
            creator_id=1,
            public=0,
            user=None,
            group=sample_group,
        )
        result = format_repo_info(repo)

        assert "👥 所属团队: Test Group (@testgroup)" in result


# =============================================================================
# TESTS: format_repo_list
# =============================================================================


class TestFormatRepoList:
    """Tests for format_repo_list function."""

    def test_with_empty_list(self):
        """Test formatting empty repositories list."""
        result = format_repo_list([])
        assert "📚 知识库列表" in result
        assert "暂无知识库" in result

    def test_with_single_repo(self, sample_repo: Repository):
        """Test formatting single repository."""
        result = format_repo_list([sample_repo])

        assert "1. Test Repository (test-repo)" in result
        assert "🆔 ID: 500" in result
        assert "📂 类型: Book" in result

    def test_with_multiple_repos(self, sample_repo: Repository, sample_repo_minimal: Repository):
        """Test formatting multiple repositories."""
        result = format_repo_list([sample_repo, sample_repo_minimal])

        assert "1. Test Repository (test-repo)" in result
        assert "2. Minimal Repository (minimal-repo)" in result

    def test_with_long_description_truncation(self, sample_repo_long_desc: Repository):
        """Test that long descriptions are truncated to 100 chars."""
        result = format_repo_list([sample_repo_long_desc])

        # Should contain truncated version with ellipsis
        assert "..." in result
        # Description line should be truncated
        desc_line = [line for line in result.split("\n") if "📝" in line][0]
        assert len(desc_line) < 150  # Reasonable truncated length

    def test_with_short_description_no_truncation(self, sample_repo: Repository):
        """Test that short descriptions are not truncated."""
        result = format_repo_list([sample_repo])

        assert "A test repository" in result
        assert "..." not in result.split("📝")[1].split("\n")[0]

    def test_with_user_owner(self, sample_repo: Repository):
        """Test repository list with user owner."""
        result = format_repo_list([sample_repo])

        assert "👤 Test User" in result

    def test_with_group_owner(self, sample_group: Group):
        """Test repository list with group owner."""
        repo = Repository(
            id=900,
            type="Book",
            slug="group-owned",
            name="Group Owned Repo",
            creator_id=1,
            public=0,
            user=None,
            group=sample_group,
        )
        result = format_repo_list([repo])

        assert "👥 Test Group" in result

    def test_with_dict_input(self):
        """Test formatting repositories from dict list."""
        repo_dict = {
            "id": 1000,
            "type": "Book",
            "slug": "dict-list-repo",
            "name": "Dict List Repo",
            "creator_id": 1,
            "public": 0,
        }
        result = format_repo_list([repo_dict])

        assert "Dict List Repo (dict-list-repo)" in result


# =============================================================================
# TESTS: format_repo_toc
# =============================================================================


class TestFormatRepoToc:
    """Tests for format_repo_toc function."""

    def test_with_empty_list(self):
        """Test formatting empty TOC."""
        result = format_repo_toc([])
        assert "📑 知识库目录" in result
        assert "暂无目录" in result

    def test_with_single_node(self):
        """Test formatting single TOC node."""
        node = TocNode(
            title="Single Document",
            slug="single",
            document_id=5000,
            depth=1,
            order=1,
        )
        result = format_repo_toc([node])

        assert "📄 Single Document (ID: 5000)" in result

    def test_with_nested_children(self, sample_toc_node: TocNode):
        """Test formatting TOC with nested children."""
        result = format_repo_toc([sample_toc_node])

        assert "📄 Root Document (ID: 3000)" in result
        assert "📄 Child Document 1 (ID: 3001)" in result
        assert "📄 Child Document 2 (ID: 3002)" in result
        assert "📄 Grandchild Document (ID: 3003)" in result

    def test_with_dict_input(self):
        """Test formatting TOC from dict list."""
        node_dict = {
            "title": "Dict Node",
            "slug": "dict-node",
            "document_id": 6000,
            "depth": 1,
            "order": 1,
        }
        result = format_repo_toc([node_dict])

        assert "📄 Dict Node (ID: 6000)" in result

    def test_indentation_for_nested_nodes(self, sample_toc_node: TocNode):
        """Test that nested nodes have proper indentation."""
        result = format_repo_toc([sample_toc_node])
        lines = result.split("\n")

        # Find the grandchild line
        grandchild_line = [l for l in lines if "Grandchild Document" in l][0]
        # Should have 4 spaces of indentation (2 levels * 2 spaces)
        assert grandchild_line.startswith("    ")


# =============================================================================
# TESTS: format_doc_info
# =============================================================================


class TestFormatDocInfo:
    """Tests for format_doc_info function."""

    def test_with_full_doc_model(self, sample_doc: Document):
        """Test formatting document with all fields."""
        result = format_doc_info(sample_doc)

        assert "📄 文档信息" in result
        assert "🆔 ID: 2000" in result
        assert "📛 标识: test-doc" in result
        assert "📖 标题: Test Document" in result
        assert "🔐 可见性: 🔒 私有" in result
        assert "🖼️ 封面: https://example.com/cover.png" in result
        assert "👤 创建者ID: 1" in result
        assert "✍️ 最后编辑者ID: 1" in result
        assert "📚 所属知识库ID: 500" in result
        assert "📊 版本: 5" in result
        assert "📝 字数: 1500" in result
        assert "👁️ 阅读数: 100" in result
        assert "❤️ 点赞数: 25" in result
        assert "💬 评论数: 10" in result
        assert "首次发布: 2024-04-02 10:00:00" in result
        assert "👤 创建者: Test User (@testuser)" in result
        assert "📚 知识库: Test Repository (test-repo)" in result

    def test_with_minimal_doc_model(self, sample_doc_minimal: Document):
        """Test formatting document with minimal fields."""
        result = format_doc_info(sample_doc_minimal)

        assert "🆔 ID: 2001" in result
        assert "📖 标题: Minimal Document" in result
        assert "🖼️ 封面" not in result
        assert "📝 字数: N/A" in result
        assert "首次发布" not in result

    def test_with_dict_input(self):
        """Test formatting document from dict."""
        doc_dict = {
            "id": 3000,
            "slug": "dict-doc",
            "title": "Dict Document",
            "body_format": 1,
            "creator_id": 1,
            "user_id": 1,
            "book_id": 500,
            "public": 1,
            "version": 1,
        }
        result = format_doc_info(doc_dict)

        assert "🆔 ID: 3000" in result
        assert "📖 标题: Dict Document" in result

    def test_last_editor_fallback_to_user_id(self):
        """Test that last_editor_id falls back to user_id when None."""
        doc = Document(
            id=4000,
            slug="fallback-doc",
            title="Fallback Document",
            body_format=1,
            creator_id=1,
            user_id=5,  # This should be used
            book_id=500,
            public=0,
            version=1,
            last_editor_id=None,  # None, should fallback to user_id
        )
        result = format_doc_info(doc)

        assert "✍️ 最后编辑者ID: 5" in result


# =============================================================================
# TESTS: format_doc_list
# =============================================================================


class TestFormatDocList:
    """Tests for format_doc_list function."""

    def test_with_empty_list(self):
        """Test formatting empty documents list."""
        result = format_doc_list([])
        assert "📄 文档列表" in result
        assert "暂无文档" in result

    def test_with_single_doc(self, sample_doc: Document):
        """Test formatting single document."""
        result = format_doc_list([sample_doc])

        assert "1. Test Document" in result
        assert "🆔 ID: 2000" in result
        assert "📛 Slug: test-doc" in result
        assert "📊 版本: 5" in result
        assert "📝 字数: 1500" in result
        assert "👁️ 100" in result
        assert "❤️ 25" in result
        assert "💬 10" in result

    def test_with_multiple_docs(self, sample_doc: Document, sample_doc_minimal: Document):
        """Test formatting multiple documents."""
        result = format_doc_list([sample_doc, sample_doc_minimal])

        assert "1. Test Document" in result
        assert "2. Minimal Document" in result

    def test_with_dict_input(self):
        """Test formatting documents from dict list."""
        doc_dict = {
            "id": 5000,
            "slug": "dict-list-doc",
            "title": "Dict List Doc",
            "body_format": 1,
            "creator_id": 1,
            "user_id": 1,
            "book_id": 500,
            "public": 0,
            "version": 1,
        }
        result = format_doc_list([doc_dict])

        assert "Dict List Doc" in result

    def test_word_count_na_when_none(self, sample_doc_minimal: Document):
        """Test that word_count shows N/A when None."""
        result = format_doc_list([sample_doc_minimal])

        assert "📝 字数: N/A" in result


# =============================================================================
# TESTS: format_search_results
# =============================================================================


class TestFormatSearchResults:
    """Tests for format_search_results function."""

    def test_with_empty_list(self):
        """Test formatting empty search results."""
        result = format_search_results([])
        assert "🔍 搜索结果" in result
        assert "未找到相关内容" in result

    def test_with_doc_type(self, sample_search_result: SearchResult):
        """Test formatting search result with doc type."""
        result = format_search_results([sample_search_result])

        assert "📄 Search Result Document" in result
        assert "📂 类型: doc" in result

    def test_with_book_type(self, sample_search_result_minimal: SearchResult):
        """Test formatting search result with book type."""
        result = format_search_results([sample_search_result_minimal])

        assert "📚 Minimal Search Result" in result
        assert "📂 类型: book" in result

    def test_with_user_type(self):
        """Test formatting search result with user type."""
        result_obj = SearchResult(
            id=6000,
            type="user",
            title="User Result",
        )
        result = format_search_results([result_obj])

        assert "👤 User Result" in result

    def test_with_group_type(self):
        """Test formatting search result with group type."""
        result_obj = SearchResult(
            id=7000,
            type="group",
            title="Group Result",
        )
        result = format_search_results([result_obj])

        assert "👥 Group Result" in result

    def test_with_unknown_type(self):
        """Test formatting search result with unknown type."""
        result_obj = SearchResult(
            id=8000,
            type="unknown",
            title="Unknown Result",
        )
        result = format_search_results([result_obj])

        assert "📌 Unknown Result" in result  # Default icon

    def test_with_long_summary_truncation(self, sample_search_result: SearchResult):
        """Test that long summaries are truncated to 150 chars."""
        result = format_search_results([sample_search_result])

        assert "..." in result

    def test_with_short_summary_no_truncation(self):
        """Test that short summaries are not truncated."""
        result_obj = SearchResult(
            id=9000,
            type="doc",
            title="Short Summary",
            summary="This is a short summary.",
        )
        result = format_search_results([result_obj])

        assert "This is a short summary." in result
        assert "..." not in result

    def test_with_all_fields(self, sample_search_result: SearchResult):
        """Test formatting search result with all optional fields."""
        result = format_search_results([sample_search_result])

        assert "🔗 https://yuque.com" in result
        assert "👤 用户: Test User (@testuser)" in result
        assert "📚 知识库: Test Repository" in result

    def test_with_dict_input(self):
        """Test formatting search results from dict list."""
        result_dict = {
            "id": 10000,
            "type": "doc",
            "title": "Dict Search Result",
        }
        result = format_search_results([result_dict])

        assert "Dict Search Result" in result


# =============================================================================
# TESTS: format_response (Dispatcher)
# =============================================================================


class TestFormatResponse:
    """Tests for format_response dispatcher function."""

    def test_with_none(self):
        """Test formatting None data."""
        result = format_response(None)
        assert result == {"content": "暂无数据"}

    def test_with_empty_list(self):
        """Test formatting empty list."""
        result = format_response([])
        assert result == {"content": "列表为空"}

    def test_with_user_model(self, sample_user: User):
        """Test dispatching User model."""
        result = format_response(sample_user)
        assert "👤 用户信息" in result["content"]

    def test_with_group_model(self, sample_group: Group):
        """Test dispatching Group model."""
        result = format_response(sample_group)
        assert "👥 团队信息" in result["content"]

    def test_with_repo_model(self, sample_repo: Repository):
        """Test dispatching Repository model."""
        result = format_response(sample_repo)
        assert "📚 知识库信息" in result["content"]

    def test_with_doc_model(self, sample_doc: Document):
        """Test dispatching Document model."""
        result = format_response(sample_doc)
        assert "📄 文档信息" in result["content"]

    def test_with_user_list_as_groups(self):
        """Test dispatching list of dicts that look like groups."""
        group_dict = {
            "id": 1,
            "login": "testgroup",
            "name": "Test Group",
            "owner_id": 1,
            "members_count": 5,
            "books_count": 3,
        }
        result = format_response([group_dict])
        assert "👥 团队列表" in result["content"]

    def test_with_group_list(self, sample_group: Group):
        """Test dispatching list of Groups."""
        result = format_response([sample_group])
        assert "👥 团队列表" in result["content"]

    def test_with_member_list(self, sample_group_member: GroupMember):
        """Test dispatching list of GroupMembers."""
        result = format_response([sample_group_member])
        assert "👥 团队成员" in result["content"]

    def test_with_repo_list(self, sample_repo: Repository):
        """Test dispatching list of Repositories."""
        result = format_response([sample_repo])
        assert "📚 知识库列表" in result["content"]

    def test_with_doc_list(self, sample_doc: Document):
        """Test dispatching list of Documents."""
        result = format_response([sample_doc])
        assert "📄 文档列表" in result["content"]

    def test_with_search_result_list(self, sample_search_result: SearchResult):
        """Test dispatching list of SearchResults."""
        result = format_response([sample_search_result])
        assert "🔍 搜索结果" in result["content"]

    def test_with_toc_list(self, sample_toc_node: TocNode):
        """Test dispatching list of TocNodes."""
        result = format_response([sample_toc_node])
        assert "📑 知识库目录" in result["content"]

    def test_with_dict_user(self, sample_user_dict: dict):
        """Test dispatching dict as user."""
        result = format_response(sample_user_dict)
        assert "👤 用户信息" in result["content"]

    def test_with_dict_group(self, sample_group_dict: dict):
        """Test dispatching dict as group."""
        result = format_response(sample_group_dict)
        assert "👥 团队信息" in result["content"]

    def test_with_dict_repo(self):
        """Test dispatching dict as repository."""
        repo_dict = {
            "id": 1,
            "type": "Book",
            "slug": "test",
            "name": "Test",
            "creator_id": 1,
            "public": 0,
        }
        result = format_response(repo_dict)
        assert "📚 知识库信息" in result["content"]

    def test_with_dict_doc(self):
        """Test dispatching dict as document."""
        doc_dict = {
            "id": 1,
            "slug": "test",
            "title": "Test",
            "body_format": 1,
            "creator_id": 1,
            "user_id": 1,
            "book_id": 1,
            "public": 0,
            "version": 1,
        }
        result = format_response(doc_dict)
        assert "📄 文档信息" in result["content"]

    def test_with_dict_list_doc(self):
        """Test dispatching list of dicts as documents."""
        doc_dict = {
            "id": 1,
            "slug": "test",
            "title": "Test",
            "body_format": 1,
            "creator_id": 1,
            "user_id": 1,
            "book_id": 1,
            "public": 0,
            "version": 1,
        }
        result = format_response([doc_dict])
        assert "📄 文档列表" in result["content"]

    def test_with_dict_list_repo(self):
        """Test dispatching list of dicts as repositories."""
        repo_dict = {
            "id": 1,
            "type": "Book",
            "slug": "test",
            "name": "Test",
            "creator_id": 1,
            "public": 0,
        }
        result = format_response([repo_dict])
        assert "📚 知识库列表" in result["content"]

    def test_with_dict_list_group(self):
        """Test dispatching list of dicts as groups."""
        group_dict = {
            "id": 1,
            "login": "test",
            "name": "Test",
            "owner_id": 1,
            "members_count": 5,
            "books_count": 3,
        }
        result = format_response([group_dict])
        assert "👥 团队列表" in result["content"]

    def test_with_unknown_type(self):
        """Test dispatching unknown type falls back to str()."""
        result = format_response("unknown string")
        assert result == {"content": "unknown string"}

    def test_with_unknown_dict(self):
        """Test dispatching unknown dict falls back to str()."""
        unknown_dict = {"foo": "bar"}
        result = format_response(unknown_dict)
        assert result == {"content": str(unknown_dict)}
