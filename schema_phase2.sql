CREATE TABLE IF NOT EXISTS articles (
    id          SERIAL PRIMARY KEY,
    url         TEXT UNIQUE NOT NULL,
    source      TEXT NOT NULL,           -- feed name, e.g. "BBC World"
    title       TEXT NOT NULL,
    summary     TEXT,
    published   TIMESTAMPTZ,
    fetched_at  TIMESTAMPTZ DEFAULT now(),
    entities    JSONB DEFAULT '[]',      -- [{"text": "...", "label": "person"}, ...]
    countries   TEXT[] DEFAULT '{}'      -- ISO3 codes the article is about
);

CREATE INDEX IF NOT EXISTS idx_articles_countries ON articles USING GIN (countries);
CREATE INDEX IF NOT EXISTS idx_articles_published ON articles (published DESC);
