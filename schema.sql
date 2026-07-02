CREATE TABLE IF NOT EXISTS events (
    id            BIGINT PRIMARY KEY,      -- GDELT GlobalEventID
    event_date    DATE        NOT NULL,
    actor1        TEXT,
    actor2        TEXT,
    cameo_code    TEXT,
    cameo_root    TEXT,                    -- 2-digit root: 18=assault, 19=fight...
    quad_class    INT,                     -- 1/2 = cooperation, 3/4 = conflict
    goldstein     REAL,                    -- -10 (worst) .. +10 (best)
    num_sources   INT,
    num_articles  INT,
    avg_tone      REAL,
    country_iso3  CHAR(3)     NOT NULL,    -- where the event happened
    place         TEXT,
    lat           REAL,
    lon           REAL,
    source_url    TEXT,
    added_at      TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_events_country_date ON events (country_iso3, event_date DESC);
CREATE INDEX IF NOT EXISTS idx_events_quad ON events (quad_class);
