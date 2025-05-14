"""icons

Revision ID: 04838360c48b
Revises: f7c078ac3000
Create Date: 2025-05-14 12:46:09.764184

"""
from pathlib import Path
from alembic import op
import sqlalchemy as sa




# revision identifiers, used by Alembic.
revision = '04838360c48b'
down_revision = 'f7c078ac3000'
branch_labels = None
depends_on = None

migration_path = Path(__file__)
migration_sql_path = migration_path.parent.parent / 'sql'
migration_sql_file = migration_path.with_suffix('.sql').name

upgrade_sql = migration_sql_path / 'upgrade' / migration_sql_file
downgrade_sql = migration_sql_path / 'downgrade' / migration_sql_file

def upgrade():
    print('===>>> Executing ', upgrade_sql)
    with open(upgrade_sql, 'r') as fp:
        op.execute(fp.read())

def downgrade():
    print('===>>> Executing ', downgrade_sql)
    with open(downgrade_sql, 'r') as fp:
        op.execute(fp.read())
