"""Add AI tables: confidence_snapshots, evidence_logs, explanation_logs, transcripts

Revision ID: a1b2c3d4e5f6
Revises: 7f3975da16e1
Create Date: 2026-07-08 05:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '7f3975da16e1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── confidence_snapshots ──────────────────────────────────────────────────
    op.create_table(
        'confidence_snapshots',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('participant_id', sa.String(length=100), nullable=False),
        sa.Column('meeting_id', sa.String(length=100), nullable=True),
        sa.Column('confidence', sa.Float(), nullable=False),
        sa.Column('evidence_type', sa.String(length=100), nullable=True),
        sa.Column('reason', sa.String(length=500), nullable=True),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        op.f('ix_confidence_snapshots_id'),
        'confidence_snapshots', ['id'], unique=False,
    )
    op.create_index(
        op.f('ix_confidence_snapshots_participant_id'),
        'confidence_snapshots', ['participant_id'], unique=False,
    )
    op.create_index(
        op.f('ix_confidence_snapshots_meeting_id'),
        'confidence_snapshots', ['meeting_id'], unique=False,
    )

    # ── evidence_logs ─────────────────────────────────────────────────────────
    op.create_table(
        'evidence_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('participant_id', sa.String(length=100), nullable=False),
        sa.Column('meeting_id', sa.String(length=100), nullable=True),
        sa.Column('evidence_type', sa.String(length=100), nullable=False),
        sa.Column('confidence_delta', sa.Float(), nullable=False),
        sa.Column('reason', sa.String(length=500), nullable=True),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        op.f('ix_evidence_logs_id'),
        'evidence_logs', ['id'], unique=False,
    )
    op.create_index(
        op.f('ix_evidence_logs_participant_id'),
        'evidence_logs', ['participant_id'], unique=False,
    )
    op.create_index(
        op.f('ix_evidence_logs_meeting_id'),
        'evidence_logs', ['meeting_id'], unique=False,
    )

    # ── explanation_logs ──────────────────────────────────────────────────────
    op.create_table(
        'explanation_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('participant_id', sa.String(length=100), nullable=False),
        sa.Column('meeting_id', sa.String(length=100), nullable=True),
        sa.Column('evidence_type', sa.String(length=100), nullable=True),
        sa.Column('explanation', sa.Text(), nullable=False),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        op.f('ix_explanation_logs_id'),
        'explanation_logs', ['id'], unique=False,
    )
    op.create_index(
        op.f('ix_explanation_logs_participant_id'),
        'explanation_logs', ['participant_id'], unique=False,
    )
    op.create_index(
        op.f('ix_explanation_logs_meeting_id'),
        'explanation_logs', ['meeting_id'], unique=False,
    )

    # ── transcripts ───────────────────────────────────────────────────────────
    op.create_table(
        'transcripts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('participant_id', sa.String(length=100), nullable=False),
        sa.Column('meeting_id', sa.String(length=100), nullable=True),
        sa.Column('speaker', sa.String(length=100), nullable=True),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('now()'),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        op.f('ix_transcripts_id'),
        'transcripts', ['id'], unique=False,
    )
    op.create_index(
        op.f('ix_transcripts_participant_id'),
        'transcripts', ['participant_id'], unique=False,
    )
    op.create_index(
        op.f('ix_transcripts_meeting_id'),
        'transcripts', ['meeting_id'], unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f('ix_transcripts_meeting_id'), table_name='transcripts')
    op.drop_index(op.f('ix_transcripts_participant_id'), table_name='transcripts')
    op.drop_index(op.f('ix_transcripts_id'), table_name='transcripts')
    op.drop_table('transcripts')

    op.drop_index(op.f('ix_explanation_logs_meeting_id'), table_name='explanation_logs')
    op.drop_index(op.f('ix_explanation_logs_participant_id'), table_name='explanation_logs')
    op.drop_index(op.f('ix_explanation_logs_id'), table_name='explanation_logs')
    op.drop_table('explanation_logs')

    op.drop_index(op.f('ix_evidence_logs_meeting_id'), table_name='evidence_logs')
    op.drop_index(op.f('ix_evidence_logs_participant_id'), table_name='evidence_logs')
    op.drop_index(op.f('ix_evidence_logs_id'), table_name='evidence_logs')
    op.drop_table('evidence_logs')

    op.drop_index(op.f('ix_confidence_snapshots_meeting_id'), table_name='confidence_snapshots')
    op.drop_index(op.f('ix_confidence_snapshots_participant_id'), table_name='confidence_snapshots')
    op.drop_index(op.f('ix_confidence_snapshots_id'), table_name='confidence_snapshots')
    op.drop_table('confidence_snapshots')
