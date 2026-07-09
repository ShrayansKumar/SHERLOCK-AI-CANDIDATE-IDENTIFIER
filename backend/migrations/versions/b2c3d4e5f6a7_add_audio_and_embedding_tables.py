"""Add audio_uploads and transcript_embeddings tables

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-07-08 06:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'audio_uploads',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('participant_id', sa.String(length=100), nullable=False),
        sa.Column('meeting_id', sa.String(length=100), nullable=True),
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('file_name', sa.String(length=255), nullable=False),
        sa.Column('file_format', sa.String(length=50), nullable=False),
        sa.Column('duration', sa.Float(), nullable=True),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        op.f('ix_audio_uploads_id'),
        'audio_uploads',
        ['id'],
        unique=False,
    )
    op.create_index(
        op.f('ix_audio_uploads_participant_id'),
        'audio_uploads',
        ['participant_id'],
        unique=False,
    )
    op.create_index(
        op.f('ix_audio_uploads_meeting_id'),
        'audio_uploads',
        ['meeting_id'],
        unique=False,
    )

    op.create_table(
        'transcript_embeddings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('transcript_id', sa.Integer(), nullable=True),
        sa.Column('participant_id', sa.String(length=100), nullable=False),
        sa.Column('meeting_id', sa.String(length=100), nullable=True),
        sa.Column('chunk_text', sa.Text(), nullable=False),
        sa.Column('embedding_vector', sa.Text(), nullable=False),
        sa.Column('model_name', sa.String(length=255), nullable=True),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        op.f('ix_transcript_embeddings_id'),
        'transcript_embeddings',
        ['id'],
        unique=False,
    )
    op.create_index(
        op.f('ix_transcript_embeddings_participant_id'),
        'transcript_embeddings',
        ['participant_id'],
        unique=False,
    )
    op.create_index(
        op.f('ix_transcript_embeddings_meeting_id'),
        'transcript_embeddings',
        ['meeting_id'],
        unique=False,
    )


def downgrade() -> None:
    op.drop_table('transcript_embeddings')
    op.drop_table('audio_uploads')
