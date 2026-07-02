CREATE TABLE IF NOT EXISTS summaries (
    iso3          CHAR(3) PRIMARY KEY,
    summary       TEXT NOT NULL,
    model         TEXT NOT NULL,
    generated_at  TIMESTAMPTZ DEFAULT now()
);
