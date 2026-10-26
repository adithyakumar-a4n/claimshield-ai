-- ClaimShield AI: SQL profiling queries (SQLite syntax).
-- Run after loading a CSV into a table named claims.

-- 1. Total records and distinct claim IDs.
SELECT COUNT(*) AS row_count,
       COUNT(DISTINCT claim_id) AS distinct_claim_ids
FROM claims;

-- 2. Missing key fields.
SELECT
  SUM(CASE WHEN claim_id IS NULL OR TRIM(claim_id) = '' THEN 1 ELSE 0 END) AS missing_claim_id,
  SUM(CASE WHEN member_id IS NULL OR TRIM(member_id) = '' THEN 1 ELSE 0 END) AS missing_member_id,
  SUM(CASE WHEN provider_id IS NULL OR TRIM(provider_id) = '' THEN 1 ELSE 0 END) AS missing_provider_id
FROM claims;

-- 3. Duplicate claim identifiers.
SELECT claim_id, COUNT(*) AS occurrences
FROM claims
GROUP BY claim_id
HAVING COUNT(*) > 1
ORDER BY occurrences DESC;

-- 4. Amount and payment consistency.
SELECT COUNT(*) AS invalid_amount_rows
FROM claims
WHERE claim_amount IS NULL OR claim_amount < 0
   OR paid_amount IS NULL OR paid_amount < 0
   OR paid_amount > claim_amount;

-- 5. Operational KPIs by status.
SELECT LOWER(claim_status) AS claim_status,
       COUNT(*) AS claim_count,
       ROUND(SUM(claim_amount), 2) AS submitted_amount,
       ROUND(SUM(paid_amount), 2) AS paid_amount
FROM claims
GROUP BY LOWER(claim_status)
ORDER BY claim_count DESC;

-- 6. Provider volume and amount summary. This is descriptive, not a fraud ranking.
SELECT provider_id,
       COUNT(*) AS claim_count,
       ROUND(SUM(claim_amount), 2) AS total_claim_amount,
       ROUND(AVG(claim_amount), 2) AS average_claim_amount
FROM claims
GROUP BY provider_id
ORDER BY claim_count DESC;
