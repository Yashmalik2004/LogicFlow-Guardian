-- ============================================================
-- MS2 Migration 001 — Create agent_run table
-- ============================================================
-- Run this against MS2's own PostgreSQL database (MS2_DATABASE_URL).
-- DO NOT run this against MS1's database.
-- ============================================================

CREATE TABLE IF NOT EXISTS agent_run (
    id               SERIAL PRIMARY KEY,

    -- References MS1's Analysis record by value (no cross-DB foreign key).
    analysis_id      INTEGER NOT NULL UNIQUE,
    -- References MS1's Project record by value.
    project_id       INTEGER NOT NULL,

    -- Current execution status within MS2's pipeline.
    status           VARCHAR(40) NOT NULL DEFAULT 'RECEIVED'
                     CHECK (status IN (
                       'RECEIVED',
                       'CLONING',
                       'VALIDATING',
                       'READY_FOR_PARSING',
                       'COMPLETED',
                       'FAILED'
                     )),

    -- Repository metadata discovered during intake.
    repository_path  TEXT,
    repository_name  TEXT,
    language         TEXT,
    framework        TEXT,
    repository_size  BIGINT,

    -- Error details when the run fails.
    error_message    TEXT,

    started_at       TIMESTAMP WITH TIME ZONE,
    completed_at     TIMESTAMP WITH TIME ZONE,
    created_at       TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_agent_run_analysis_id ON agent_run (analysis_id);
CREATE INDEX IF NOT EXISTS idx_agent_run_project_id  ON agent_run (project_id);
