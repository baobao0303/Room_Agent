CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS intake (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    source TEXT,
    state TEXT NOT NULL DEFAULT 'New',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS story (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    intake_id INTEGER REFERENCES intake(id) ON DELETE SET NULL,
    title TEXT NOT NULL,
    description TEXT,
    state TEXT NOT NULL DEFAULT 'New',
    assigned_to TEXT,
    priority TEXT NOT NULL DEFAULT 'P2',
    verify_command TEXT,
    last_verified_at TEXT,
    last_verified_result TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS decision (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Proposed',
    context TEXT,
    decision TEXT,
    consequences TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS backlog (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    priority TEXT NOT NULL DEFAULT 'P2',
    state TEXT NOT NULL DEFAULT 'New',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

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

CREATE TABLE IF NOT EXISTS tool (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    command TEXT NOT NULL,
    description TEXT,
    responsibility TEXT,
    args TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS intervention (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    target_type TEXT NOT NULL,
    target_id   INTEGER NOT NULL,
    actor       TEXT NOT NULL,
    action      TEXT DEFAULT 'approved',
    reason      TEXT NOT NULL,
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS work_item (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    type                 TEXT    NOT NULL
                         CHECK(type IN (
                             'Epic', 'Feature', 'User Story', 'Technical Story', 'Task', 'Bug', 'Testcase'
                         )),
    title                TEXT    NOT NULL,
    description          TEXT,
    state                TEXT    NOT NULL DEFAULT 'New'
                         CHECK(state IN (
                             'New', 'Accepted', 'Active', 'Resolved', 'Closed', 'Blocked', 'Removed'
                         )),
    assigned_to          TEXT,
    story_points         INTEGER CHECK(story_points IS NULL OR story_points >= 0),
    remaining_work       REAL    CHECK(remaining_work IS NULL OR remaining_work >= 0),
    priority             TEXT    NOT NULL DEFAULT 'P2'
                         CHECK(priority IN ('P0', 'P1', 'P2', 'P3')),
    severity             TEXT    CHECK(severity IS NULL OR severity IN ('Low', 'Medium', 'High', 'Critical')),
    parent_id            INTEGER REFERENCES work_item(id) ON DELETE SET NULL,
    area_path            TEXT,
    iteration_path       TEXT,
    tags                 TEXT,
    acceptance_criteria  TEXT,
    repro_steps          TEXT,
    actual_result        TEXT,
    expected_result      TEXT,
    steps                TEXT,
    source               TEXT    NOT NULL DEFAULT 'local',
    created_by_profile   TEXT,
    assigned_to_profile  TEXT,
    created_at           TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at           TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_work_item_type ON work_item(type);
CREATE INDEX IF NOT EXISTS idx_work_item_state ON work_item(state);
CREATE INDEX IF NOT EXISTS idx_work_item_parent ON work_item(parent_id);
CREATE INDEX IF NOT EXISTS idx_work_item_assigned ON work_item(assigned_to);

CREATE TABLE IF NOT EXISTS harness_experience (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    domain               TEXT    NOT NULL,
    work_item_id         INTEGER REFERENCES work_item(id) ON DELETE SET NULL,
    cue                  TEXT    NOT NULL,
    lesson               TEXT    NOT NULL,
    evidence             TEXT    NOT NULL,
    confidence           TEXT    NOT NULL DEFAULT 'medium'
                         CHECK(confidence IN ('low', 'medium', 'high')),
    harness_patch        TEXT,
    created_at           TEXT    NOT NULL DEFAULT (datetime('now')),
    pattern_hash         TEXT,
    successful_harness   TEXT,
    failure_trajectories TEXT
);

CREATE INDEX IF NOT EXISTS idx_harness_experience_domain ON harness_experience(domain);
CREATE INDEX IF NOT EXISTS idx_harness_experience_work_item ON harness_experience(work_item_id);
CREATE INDEX IF NOT EXISTS idx_exp_domain_pattern ON harness_experience(domain, pattern_hash);

INSERT OR IGNORE INTO schema_version (version) VALUES (6);
INSERT OR IGNORE INTO schema_version (version) VALUES (7);
INSERT OR IGNORE INTO schema_version (version) VALUES (8);

