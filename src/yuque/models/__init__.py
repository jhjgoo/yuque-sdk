"""Base models for Yuque API responses."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class BaseYuqueModel(BaseModel):
    """Base model for all Yuque API responses."""

    model_config = {
        "populate_by_name": True,
        "from_attributes": True,
    }


class User(BaseYuqueModel):
    """User model representing a Yuque user."""

    id: int = Field(..., description="User ID")
    login: str = Field(..., description="User login name")
    name: str = Field(..., description="User display name")
    avatar_url: str | None = Field(None, description="User avatar URL")
    email: str | None = Field(None, description="User email")
    created_at: datetime | None = Field(None, description="Account creation time")
    updated_at: datetime | None = Field(None, description="Last update time")
    html_url: str | None = Field(None, description="User profile URL")


class Group(BaseYuqueModel):
    """Group model representing a Yuque group/organization."""

    id: int = Field(..., description="Group ID")
    login: str = Field(..., description="Group login name (slug)")
    name: str = Field(..., description="Group display name")
    description: str | None = Field(None, description="Group description")
    avatar_url: str | None = Field(None, description="Group avatar URL")
    owner_id: int = Field(..., description="Group owner user ID")
    created_at: datetime | None = Field(None, description="Group creation time")
    updated_at: datetime | None = Field(None, description="Last update time")
    members_count: int = Field(0, description="Number of members")
    books_count: int = Field(0, description="Number of knowledge bases (books)")


class GroupMember(BaseYuqueModel):
    """Group member model."""

    id: int = Field(..., description="Member record ID")
    group_id: int = Field(..., description="Group ID")
    user_id: int = Field(..., description="User ID")
    role: int = Field(..., description="Member role (0: admin, 1: member, 2: read-only)")
    created_at: datetime | None = Field(None, description="Membership creation time")
    user: User | None = Field(None, description="User details")


class Repository(BaseYuqueModel):
    """Repository (Knowledge Base/Book) model."""

    id: int = Field(..., description="Repository ID")
    type: str = Field(..., description="Repository type (Book or Space)")
    slug: str = Field(..., description="Repository slug (identifier)")
    name: str = Field(..., description="Repository name")
    description: str | None = Field(None, description="Repository description")
    creator_id: int = Field(..., description="Creator user ID")
    public: int = Field(..., description="Public level (0: private, 1: public, 2: enterprise-wide)")
    has_toc: bool = Field(False, description="Whether table of contents exists")
    toc_template: str | None = Field(None, description="TOC template")
    logo: str | None = Field(None, description="Repository logo URL")
    default_doc_id: int | None = Field(None, description="Default document ID")
    nav_config: dict[str, Any] | None = Field(None, description="Navigation configuration")
    created_at: datetime | None = Field(None, description="Repository creation time")
    updated_at: datetime | None = Field(None, description="Last update time")
    user: User | None = Field(None, description="Creator user details")
    group: Group | None = Field(None, description="Parent group details")


class Document(BaseYuqueModel):
    """Document model representing a Yuque document."""

    id: int = Field(..., description="Document ID")
    slug: str = Field(..., description="Document slug (identifier)")
    title: str = Field(..., description="Document title")
    body: str | None = Field(None, description="Document body content")
    body_format: int = Field(..., description="Body format (1: markdown, 2: HTML, 3: lake)")
    creator_id: int = Field(..., description="Creator user ID")
    user_id: int = Field(..., description="User ID")
    book_id: int = Field(..., description="Parent repository (book) ID")
    public: int = Field(0, description="Public level (0: private, 1: public, 2: enterprise-wide)")
    read_count: int = Field(0, description="Read count")
    likes_count: int = Field(0, description="Likes count")
    comments_count: int = Field(0, description="Comments count")
    version: int = Field(1, description="Document version number")
    draft_version: int | None = Field(None, description="Draft version number")
    created_at: datetime | None = Field(None, description="Document creation time")
    updated_at: datetime | None = Field(None, description="Last update time")
    published_at: datetime | None = Field(None, description="Published time")
    first_published_at: datetime | None = Field(None, description="First published time")
    last_editor_id: int | None = Field(None, description="Last editor user ID")
    word_count: int | None = Field(None, description="Word count")
    cover: str | None = Field(None, description="Document cover image URL")
    user: User | None = Field(None, description="Creator user details")
    book: Repository | None = Field(None, description="Parent repository details")


class DocumentVersion(BaseYuqueModel):
    """Document version model."""

    id: int = Field(..., description="Version ID")
    document_id: int = Field(..., description="Document ID")
    content: str = Field(..., description="Version content")
    description: str | None = Field(None, description="Version description")
    created_at: datetime | None = Field(None, description="Version creation time")


class TocNode(BaseYuqueModel):
    """Table of Contents node model."""

    title: str = Field(..., description="Node title")
    slug: str = Field(..., description="Node slug")
    document_id: int = Field(..., description="Document ID")
    parent_id: int | None = Field(None, description="Parent node ID")
    depth: int = Field(1, description="Depth level (1: root, 2: nested)")
    order: int = Field(1, description="Display order")
    children: list[TocNode] | None = Field(None, description="Child nodes")


class SearchResult(BaseYuqueModel):
    """Search result model."""

    id: int = Field(..., description="Result ID")
    type: str = Field(..., description="Result type (doc, book, user, group)")
    title: str = Field(..., description="Result title")
    summary: str | None = Field(None, description="Result summary/excerpt")
    url: str | None = Field(None, description="Result URL")
    user: User | None = Field(None, description="Related user")
    book: Repository | None = Field(None, description="Related repository")
    document: Document | None = Field(None, description="Related document")


class PaginationMeta(BaseModel):
    """Pagination metadata model."""

    page: int = Field(1, description="Current page number")
    per_page: int = Field(20, description="Items per page")
    total: int = Field(0, description="Total items count")
    total_pages: int = Field(0, description="Total pages count")


class PaginatedResponse(BaseModel):
    """Generic paginated response wrapper."""

    data: list[Any] = Field(..., description="Response data items")
    meta: PaginationMeta | None = Field(None, description="Pagination metadata")
