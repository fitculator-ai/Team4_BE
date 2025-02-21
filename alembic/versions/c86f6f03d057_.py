"""empty message

Revision ID: c86f6f03d057
Revises: 
Create Date: 2025-02-21 11:04:51.871087

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'c86f6f03d057'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # 'users' 테이블에서 'token' 컬럼의 nullable을 True로 변경
    op.alter_column('users', 'token', existing_type=sa.VARCHAR(), nullable=True)

def downgrade():
    # 'users' 테이블에서 'token' 컬럼의 nullable을 False로 변경 (되돌리기)
    op.alter_column('users', 'token', existing_type=sa.VARCHAR(), nullable=False)