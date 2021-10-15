"""remove _content

Revision ID: a31f35e95704
Revises: 32b12866f6a2
Create Date: 2021-10-15 15:12:54.633443

"""
from pathlib import Path
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a31f35e95704'
down_revision = '32b12866f6a2'
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
