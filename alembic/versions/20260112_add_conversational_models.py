"""Add conversational models

Revision ID: 20260112_conversational
Create Date: 2026-01-12

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20260112_conversational'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create conversations table
    op.create_table('conversations',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('user_id', sa.String(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_conversations_user_id'), 'conversations', ['user_id'], unique=False)

    # Create messages table
    op.create_table('messages',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('conversation_id', sa.String(), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('message_metadata', sa.JSON(), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_messages_conversation_id'), 'messages', ['conversation_id'], unique=False)

    # Create custom_tools table
    op.create_table('custom_tools',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('input_schema', sa.Text(), nullable=False),
        sa.Column('definition', sa.JSON(), nullable=False),
        sa.Column('created_by', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_custom_tools_created_by'), 'custom_tools', ['created_by'], unique=False)
    op.create_index(op.f('ix_custom_tools_is_active'), 'custom_tools', ['is_active'], unique=False)
    op.create_index(op.f('ix_custom_tools_name'), 'custom_tools', ['name'], unique=True)

    # Create workflow_templates table
    op.create_table('workflow_templates',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('definition', sa.JSON(), nullable=False),
        sa.Column('created_by', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_public', sa.Boolean(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('execution_count', sa.Integer(), nullable=True),
        sa.Column('last_executed_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_workflow_templates_created_by'), 'workflow_templates', ['created_by'], unique=False)
    op.create_index(op.f('ix_workflow_templates_is_active'), 'workflow_templates', ['is_active'], unique=False)
    op.create_index(op.f('ix_workflow_templates_is_public'), 'workflow_templates', ['is_public'], unique=False)
    op.create_index(op.f('ix_workflow_templates_name'), 'workflow_templates', ['name'], unique=False)


def downgrade():
    op.drop_table('workflow_templates')
    op.drop_table('custom_tools')
    op.drop_table('messages')
    op.drop_table('conversations')
