DROP TABLE IF EXISTS problems;

CREATE TABLE problems (
  id                BIGSERIAL PRIMARY KEY,
  tracking_id       TEXT UNIQUE NOT NULL,
  student_name      TEXT NOT NULL,
  student_email     TEXT DEFAULT '',
  description       TEXT NOT NULL,
  category          TEXT NOT NULL DEFAULT 'Other',
  confidence        FLOAT DEFAULT 0.75,
  reason            TEXT DEFAULT '',
  department        TEXT NOT NULL DEFAULT 'General Administration',
  status            TEXT NOT NULL DEFAULT 'Submitted',
  resolution        TEXT DEFAULT '',
  escalation_level  INT DEFAULT 0,
  current_authority TEXT DEFAULT 'Department',
  escalation_reason TEXT DEFAULT '',
  dispute_count     INT DEFAULT 0,
  priority          TEXT DEFAULT 'normal',
  is_medical        BOOLEAN DEFAULT FALSE,
  is_repeat         BOOLEAN DEFAULT FALSE,
  created_at        TIMESTAMPTZ DEFAULT NOW(),
  updated_at        TIMESTAMPTZ DEFAULT NOW(),
  escalated_at      TIMESTAMPTZ
);

CREATE INDEX ON problems (tracking_id);
CREATE INDEX ON problems (status);
CREATE INDEX ON problems (escalation_level);
CREATE INDEX ON problems (priority);
CREATE INDEX ON problems (student_email);
