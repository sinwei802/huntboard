-- Warboard SQLite schema draft v0
-- Matches references/warboard-schema.md
-- NOT yet runtime-enforced in the hunting skill loop.

PRAGMA foreign_keys = ON;

CREATE TABLE engagements (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('draft', 'active', 'paused', 'closed')),
  mode TEXT NOT NULL CHECK (mode IN ('ctf', 'pentest', 'other')),
  scope_notes TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE INDEX idx_engagements_status ON engagements(status);

CREATE TABLE realms (
  id TEXT PRIMARY KEY,
  engagement_id TEXT NOT NULL REFERENCES engagements(id),
  name TEXT NOT NULL,
  kind TEXT NOT NULL CHECK (kind IN ('lab', 'corp', 'cloud', 'segment', 'other')),
  notes TEXT,
  created_at TEXT NOT NULL
);

CREATE INDEX idx_realms_engagement ON realms(engagement_id);
CREATE INDEX idx_realms_engagement_kind ON realms(engagement_id, kind);

CREATE TABLE assets (
  id TEXT PRIMARY KEY,
  engagement_id TEXT NOT NULL REFERENCES engagements(id),
  realm_id TEXT NOT NULL REFERENCES realms(id),
  hostname TEXT,
  address TEXT,
  status TEXT NOT NULL CHECK (status IN ('unknown', 'reachable', 'mapped', 'foothold', 'user', 'root', 'oos')),
  os_guess TEXT,
  notes TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  CHECK (hostname IS NOT NULL OR address IS NOT NULL)
);

CREATE INDEX idx_assets_engagement ON assets(engagement_id);
CREATE INDEX idx_assets_realm ON assets(realm_id);
CREATE INDEX idx_assets_engagement_status ON assets(engagement_id, status);
CREATE INDEX idx_assets_address ON assets(address);

CREATE TABLE surfaces (
  id TEXT PRIMARY KEY,
  asset_id TEXT NOT NULL REFERENCES assets(id),
  engagement_id TEXT NOT NULL REFERENCES engagements(id),
  kind TEXT NOT NULL,
  port INTEGER,
  path_or_name TEXT,
  banner_or_product TEXT,
  status TEXT NOT NULL CHECK (status IN ('unseen', 'seen', 'fingerprinted', 'interesting', 'oos')),
  notes TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE INDEX idx_surfaces_asset ON surfaces(asset_id);
CREATE INDEX idx_surfaces_engagement_status ON surfaces(engagement_id, status);
CREATE INDEX idx_surfaces_engagement_port ON surfaces(engagement_id, port);

CREATE TABLE identities (
  id TEXT PRIMARY KEY,
  engagement_id TEXT NOT NULL REFERENCES engagements(id),
  realm_id TEXT REFERENCES realms(id),
  label TEXT NOT NULL,
  kind TEXT NOT NULL CHECK (kind IN ('user', 'service', 'role', 'anonymous', 'other')),
  privilege_band TEXT NOT NULL CHECK (privilege_band IN ('none', 'low', 'user', 'admin', 'system', 'unknown')),
  asset_id TEXT REFERENCES assets(id),
  notes TEXT,
  created_at TEXT NOT NULL
);

CREATE INDEX idx_identities_engagement ON identities(engagement_id);
CREATE INDEX idx_identities_realm ON identities(realm_id);
CREATE INDEX idx_identities_kind ON identities(kind);

CREATE TABLE loot (
  id TEXT PRIMARY KEY,
  engagement_id TEXT NOT NULL REFERENCES engagements(id),
  kind TEXT NOT NULL CHECK (kind IN ('credential', 'hash', 'token', 'ticket', 'file', 'note', 'other')),
  sensitivity TEXT NOT NULL CHECK (sensitivity IN ('low', 'medium', 'high', 'critical')),
  label TEXT NOT NULL,
  storage_ref TEXT,
  source_asset_id TEXT REFERENCES assets(id),
  source_surface_id TEXT REFERENCES surfaces(id),
  identity_id TEXT REFERENCES identities(id),
  notes TEXT,
  created_at TEXT NOT NULL
);

CREATE INDEX idx_loot_engagement_kind ON loot(engagement_id, kind);
CREATE INDEX idx_loot_sensitivity ON loot(sensitivity);
CREATE INDEX idx_loot_source_asset ON loot(source_asset_id);

CREATE TABLE edges (
  id TEXT PRIMARY KEY,
  engagement_id TEXT NOT NULL REFERENCES engagements(id),
  kind TEXT NOT NULL CHECK (kind IN (
    'hosts', 'exposes', 'authenticates_as', 'yields', 'reaches',
    'supports', 'blocks', 'derived_from', 'other'
  )),
  src_type TEXT NOT NULL,
  src_id TEXT NOT NULL,
  dst_type TEXT NOT NULL,
  dst_id TEXT NOT NULL,
  label TEXT,
  created_at TEXT NOT NULL
);

CREATE INDEX idx_edges_engagement_kind ON edges(engagement_id, kind);
CREATE INDEX idx_edges_src ON edges(src_type, src_id);
CREATE INDEX idx_edges_dst ON edges(dst_type, dst_id);

CREATE TABLE hypotheses (
  id TEXT PRIMARY KEY,
  engagement_id TEXT NOT NULL REFERENCES engagements(id),
  claim TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('open', 'supported', 'refuted', 'scoped_out')),
  related_asset_id TEXT REFERENCES assets(id),
  related_surface_id TEXT REFERENCES surfaces(id),
  expect TEXT,
  kill_if TEXT,
  notes TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE INDEX idx_hypotheses_engagement_status ON hypotheses(engagement_id, status);

CREATE TABLE goals (
  id TEXT PRIMARY KEY,
  engagement_id TEXT NOT NULL REFERENCES engagements(id),
  title TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('proposed', 'active', 'achieved', 'abandoned', 'blocked')),
  success_criteria TEXT,
  notes TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);

CREATE INDEX idx_goals_engagement_status ON goals(engagement_id, status);

CREATE TABLE focus (
  id TEXT PRIMARY KEY,
  engagement_id TEXT NOT NULL UNIQUE REFERENCES engagements(id),
  phase TEXT NOT NULL CHECK (phase IN ('orient', 'map', 'probe', 'exploit', 'persist', 'decide', 'idle')),
  summary TEXT,
  active_asset_id TEXT REFERENCES assets(id),
  active_goal_id TEXT REFERENCES goals(id),
  pending_decision_json TEXT,
  updated_at TEXT NOT NULL
);

CREATE TABLE events (
  id TEXT PRIMARY KEY,
  engagement_id TEXT NOT NULL REFERENCES engagements(id),
  kind TEXT NOT NULL CHECK (kind IN (
    'observation', 'action', 'decision', 'proposal', 'state_change', 'note', 'error'
  )),
  body_json TEXT NOT NULL,
  actor TEXT NOT NULL CHECK (actor IN ('agent', 'commander', 'system')),
  related_focus_id TEXT REFERENCES focus(id),
  created_at TEXT NOT NULL
);

CREATE INDEX idx_events_engagement_created ON events(engagement_id, created_at);
CREATE INDEX idx_events_engagement_kind ON events(engagement_id, kind);
