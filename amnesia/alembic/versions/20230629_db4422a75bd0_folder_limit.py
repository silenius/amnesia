"""folder limit

Revision ID: db4422a75bd0
Revises: f42e6509f5f1
Create Date: 2023-06-29 11:26:04.675339

"""
from pathlib import Path
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'db4422a75bd0'
down_revision = 'f42e6509f5f1'
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
