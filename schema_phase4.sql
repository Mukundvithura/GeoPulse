CREATE TABLE IF NOT EXISTS relations (
    id          SERIAL PRIMARY KEY,
    article_id  INT REFERENCES articles(id) ON DELETE CASCADE,
    actor       TEXT NOT NULL,
    action      TEXT NOT NULL,
    target      TEXT,
    location    TEXT,
    instrument  TEXT
);
CREATE INDEX IF NOT EXISTS idx_relations_article ON relations (article_id);

-- precomputed related-countries so the cloud deploy works without Memgraph
CREATE TABLE IF NOT EXISTS related_countries (
    iso3     CHAR(3) NOT NULL,
    other    CHAR(3) NOT NULL,
    links    INT NOT NULL,
    via      TEXT[] DEFAULT '{}',
    PRIMARY KEY (iso3, other)
);
