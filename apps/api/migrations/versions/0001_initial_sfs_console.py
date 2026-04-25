from __future__ import annotations

from alembic import op


revision = "0001_initial_sfs_console"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS production_requests (
          id text PRIMARY KEY,
          request_type text NOT NULL CHECK (
            request_type IN ('new_episode', 'revise_episode', 'publish_only', 'metadata_update')
          ),
          episode_slug text NOT NULL,
          character_slug text NOT NULL,
          format_profile_slug text NOT NULL,
          output_target text NOT NULL,
          reference_path text NOT NULL,
          completion_criteria text NOT NULL,
          creative_brief text NOT NULL,
          markdown text NOT NULL,
          status text NOT NULL DEFAULT 'draft',
          paperclip_issue_ref text,
          created_at timestamptz NOT NULL DEFAULT now(),
          updated_at timestamptz NOT NULL DEFAULT now()
        );

        CREATE INDEX IF NOT EXISTS idx_production_requests_created_at
          ON production_requests (created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_production_requests_episode_slug
          ON production_requests (episode_slug);

        CREATE TABLE IF NOT EXISTS delivery_tokens (
          id text PRIMARY KEY,
          episode_slug text NOT NULL,
          token_hash text NOT NULL UNIQUE,
          status text NOT NULL CHECK (status IN ('active', 'revoked')),
          max_accesses integer NOT NULL DEFAULT 5,
          access_count integer NOT NULL DEFAULT 0,
          expires_at timestamptz NOT NULL,
          created_at timestamptz NOT NULL DEFAULT now(),
          revoked_at timestamptz,
          last_accessed_at timestamptz
        );

        ALTER TABLE delivery_tokens
          ADD COLUMN IF NOT EXISTS max_accesses integer NOT NULL DEFAULT 5;
        ALTER TABLE delivery_tokens
          ADD COLUMN IF NOT EXISTS access_count integer NOT NULL DEFAULT 0;
        ALTER TABLE delivery_tokens
          ADD COLUMN IF NOT EXISTS last_accessed_at timestamptz;

        CREATE INDEX IF NOT EXISTS idx_delivery_tokens_episode_slug
          ON delivery_tokens (episode_slug);
        CREATE INDEX IF NOT EXISTS idx_delivery_tokens_status_expires_at
          ON delivery_tokens (status, expires_at);

        CREATE TABLE IF NOT EXISTS client_revision_requests (
          id text PRIMARY KEY,
          token_id text NOT NULL,
          episode_slug text NOT NULL,
          requester_name text NOT NULL,
          requester_email text NOT NULL,
          timestamp_note text NOT NULL,
          message text NOT NULL,
          status text NOT NULL DEFAULT 'received',
          paperclip_issue_ref text,
          created_at timestamptz NOT NULL DEFAULT now(),
          updated_at timestamptz NOT NULL DEFAULT now()
        );

        CREATE INDEX IF NOT EXISTS idx_client_revision_requests_created_at
          ON client_revision_requests (created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_client_revision_requests_episode_slug
          ON client_revision_requests (episode_slug);
        CREATE INDEX IF NOT EXISTS idx_client_revision_requests_token_id
          ON client_revision_requests (token_id);

        CREATE TABLE IF NOT EXISTS audit_logs (
          id text PRIMARY KEY,
          action text NOT NULL,
          entity_type text NOT NULL,
          entity_id text NOT NULL,
          payload jsonb NOT NULL DEFAULT '{}'::jsonb,
          actor text NOT NULL DEFAULT 'operator',
          created_at timestamptz NOT NULL DEFAULT now()
        );

        CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at
          ON audit_logs (created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_audit_logs_entity
          ON audit_logs (entity_type, entity_id);
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DROP TABLE IF EXISTS audit_logs;
        DROP TABLE IF EXISTS client_revision_requests;
        DROP TABLE IF EXISTS delivery_tokens;
        DROP TABLE IF EXISTS production_requests;
        """
    )
