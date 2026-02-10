# PURPOSE: Create initial sources/documents/sections tables.
# DEPENDENCIES: Alembic, SQLAlchemy
# MODIFICATION NOTES: MVP initial schema with search vector.

from alembic import op
import sqlalchemy as sa


revision = "0001_create_documents"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # PURPOSE: Apply initial schema for sources, documents, and sections.
    # DEPENDENCIES: Alembic
    # MODIFICATION NOTES: MVP initial migration.
    op.create_table(
        "sources",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=200), nullable=False, unique=True),
        sa.Column("source_type", sa.String(length=50), nullable=False),
        sa.Column("base_url", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "documents",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("source_id", sa.Integer(), sa.ForeignKey("sources.id"), nullable=False),
        sa.Column("title", sa.String(length=300), nullable=False),
        sa.Column("doc_type", sa.String(length=50), nullable=False),
        sa.Column("path", sa.String(length=500), nullable=True),
        sa.Column("url", sa.String(length=500), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_table(
        "sections",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("document_id", sa.Integer(), sa.ForeignKey("documents.id"), nullable=False),
        sa.Column("section_title", sa.String(length=300), nullable=True),
        sa.Column("page_number", sa.Integer(), nullable=True),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("raw_text", sa.Text(), nullable=False),
        sa.Column("normalized_text", sa.Text(), nullable=False),
        sa.Column("search_vector", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
    )

    op.create_index("ix_sections_search_vector", "sections", ["search_vector"])


def downgrade() -> None:
    # PURPOSE: Roll back initial schema.
    # DEPENDENCIES: Alembic
    # MODIFICATION NOTES: MVP downgrade path.
    op.drop_index("ix_sections_search_vector", table_name="sections")
    op.drop_table("sections")
    op.drop_table("documents")
    op.drop_table("sources")
