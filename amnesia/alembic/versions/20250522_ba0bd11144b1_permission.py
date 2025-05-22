"""permission

Revision ID: ba0bd11144b1
Revises: 04838360c48b
Create Date: 2025-05-22 10:16:50.174557

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text


# revision identifiers, used by Alembic.
revision = 'ba0bd11144b1'
down_revision = '04838360c48b'
branch_labels = None
depends_on = None

def upgrade():
    conn = op.get_bind()
    
    conn.execute(text("INSERT INTO permission(name, enabled, description) VALUES('browse_accounts', 'true', 'Browse accounts')"))

    conn.execute(text("INSERT INTO permission(name, enabled, description) VALUES('manage_accounts', 'true', 'Manage accounts')"))

    conn.execute(text("INSERT INTO permission(name, enabled, description) VALUES('browse_folder', 'true', 'Browse folder')"))

def downgrade():
    conn = op.get_bind()
    
    conn.execute(text("DELETE FROM acl WHERE permission_id IN (SELECT id FROM permission WHERE name IN ('browse_accounts', 'manage_accounts', 'browse_folder'))"))
    
    conn.execute(text("DELETE FROM permission WHERE name IN ('browse_accounts', 'manage_accounts', 'browse_folder')"))
