-- Harness v0 schema - migration 008
-- Harmonize trace table schema across SQL files, Python tools, and harness-cli (G-OBS-1)

CREATE TABLE IF NOT EXISTS trace (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at       TEXT    NOT NULL DEFAULT (datetime('now')),
    task_summary     TEXT    NOT NULL,
    intake_id        INTEGER REFERENCES intake(id),
    story_id         TEXT    REFERENCES story(id) ON DELETE CASCADE,
    agent            TEXT,
    actions_taken    TEXT,       -- JSON array
    files_read       TEXT,       -- JSON array
    files_changed    TEXT,       -- JSON array
    decisions_made   TEXT,       -- JSON array
    errors           TEXT,       -- JSON array
    outcome          TEXT
                     CHECK(outcome IN (
                       'completed','blocked','partial','failed'
                     )),
    duration_seconds INTEGER,
    token_estimate   INTEGER,
    harness_friction TEXT,
    notes            TEXT,
    run_id           TEXT
);

CREATE INDEX IF NOT EXISTS idx_trace_run_id ON trace(run_id);
CREATE INDEX IF NOT EXISTS idx_trace_story_id ON trace(story_id);
CREATE INDEX IF NOT EXISTS idx_trace_created_at ON trace(created_at);

INSERT OR IGNORE INTO schema_version (version) VALUES (8);
