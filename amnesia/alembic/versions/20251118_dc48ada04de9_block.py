"""block

Revision ID: dc48ada04de9
Revises: ba0bd11144b1
Create Date: 2025-11-18 15:41:40.707853

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text


# revision identifiers, used by Alembic.
revision = 'dc48ada04de9'
down_revision = 'ba0bd11144b1'
branch_labels = None
depends_on = None

def upgrade():
    conn = op.get_bind()
    conn.execute(text("ALTER TABLE document ADD is_block BOOLEAN NOT NULL DEFAULT FALSE"))
    conn.execute(text("CREATE INDEX idx_document_is_block ON document (is_block) WHERE is_block IS TRUE"))

def downgrade():
    conn = op.get_bind()
    conn.execute(text("ALTER TABLE document DROP is_block"))
    conn.execute(text("DROP INDEX IF EXISTS idx_document_is_block"))
