"""create users and orders tables

Revision ID: 0001
Revises: 
Create Date: 2025-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy.dialects.postgresql as pg

# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    """Применить миграцию: создать тип enum и таблицы users и orders."""
    # create enum type
    order_status = pg.ENUM('PENDING','PAID','SHIPPED','CANCELED', name='orderstatus')
    order_status.create(op.get_bind(), checkfirst=True)

    # users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('email', sa.String(), nullable=False, unique=True, index=True),
        sa.Column('hashed_password', sa.String(), nullable=False),
    )

    # orders table
    op.create_table(
        'orders',
        sa.Column('id', pg.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False, index=True),
        sa.Column('items', pg.JSONB, nullable=False),
        sa.Column('total_price', sa.Float(), nullable=False),
        sa.Column('status', sa.Enum('PENDING','PAID','SHIPPED','CANCELED', name='orderstatus'), nullable=False, server_default='PENDING'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    )

def downgrade():
    """Откатить миграцию: удалить таблицы orders, users и тип enum."""
    op.drop_table('orders')
    op.drop_table('users')
    order_status = pg.ENUM('PENDING','PAID','SHIPPED','CANCELED', name='orderstatus')
    order_status.drop(op.get_bind(), checkfirst=True)
