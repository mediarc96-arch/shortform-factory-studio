from __future__ import annotations

from alembic import op


revision = "0002_paperclip_sync"
down_revision = "0001_initial_sfs_console"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE client_revision_requests
          ADD COLUMN IF NOT EXISTS paperclip_status text;
        ALTER TABLE client_revision_requests
          ADD COLUMN IF NOT EXISTS paperclip_priority text;
        ALTER TABLE client_revision_requests
          ADD COLUMN IF NOT EXISTS paperclip_title text;
        ALTER TABLE client_revision_requests
          ADD COLUMN IF NOT EXISTS paperclip_updated_at text;
        ALTER TABLE client_revision_requests
          ADD COLUMN IF NOT EXISTS paperclip_latest_comment text;
        ALTER TABLE client_revision_requests
          ADD COLUMN IF NOT EXISTS paperclip_latest_comment_at text;
        ALTER TABLE client_revision_requests
          ADD COLUMN IF NOT EXISTS paperclip_synced_at timestamptz;
        ALTER TABLE client_revision_requests
          ADD COLUMN IF NOT EXISTS paperclip_sync_error text;

        CREATE INDEX IF NOT EXISTS idx_client_revision_requests_paperclip_status
          ON client_revision_requests (paperclip_status);
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP INDEX IF EXISTS idx_client_revision_requests_paperclip_status;
        ALTER TABLE client_revision_requests
          DROP COLUMN IF EXISTS paperclip_sync_error,
          DROP COLUMN IF EXISTS paperclip_synced_at,
          DROP COLUMN IF EXISTS paperclip_latest_comment_at,
          DROP COLUMN IF EXISTS paperclip_latest_comment,
          DROP COLUMN IF EXISTS paperclip_updated_at,
          DROP COLUMN IF EXISTS paperclip_title,
          DROP COLUMN IF EXISTS paperclip_priority,
          DROP COLUMN IF EXISTS paperclip_status;
        """
    )
