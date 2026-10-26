-- ClaimShield AI: portable SQLite-compatible schema for synthetic/demo claims.
-- Amounts are stored as REAL for an analytics demo; production financial systems
-- should use an exact decimal type and currency-aware validation.
CREATE TABLE IF NOT EXISTS claims (
    claim_id TEXT NOT NULL,
    member_id TEXT,
    provider_id TEXT,
    service_date TEXT,
    submission_date TEXT,
    procedure_code TEXT,
    diagnosis_group TEXT,
    place_of_service TEXT,
    claim_amount REAL,
    paid_amount REAL,
    claim_status TEXT,
    reviewed_by_human INTEGER,
    source_is_synthetic INTEGER NOT NULL DEFAULT 1,
    PRIMARY KEY (claim_id)
);

CREATE INDEX IF NOT EXISTS idx_claims_provider_id ON claims(provider_id);
CREATE INDEX IF NOT EXISTS idx_claims_service_date ON claims(service_date);
CREATE INDEX IF NOT EXISTS idx_claims_status ON claims(claim_status);
