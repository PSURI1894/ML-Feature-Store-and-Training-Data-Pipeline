-- Backfill run-state table. One row per backfill request; partition progress
-- tracked in a child table so large backfills resume from the last good day.

CREATE TABLE IF NOT EXISTS feature_store.backfill_runs (
    run_id          STRING    NOT NULL,
    feature_view    STRING    NOT NULL,
    start_date      DATE      NOT NULL,
    end_date        DATE      NOT NULL,
    status          STRING    NOT NULL,   -- pending|running|completed|failed
    rows_written    INT64     DEFAULT 0,
    requested_by    STRING,
    created_at      TIMESTAMP NOT NULL,
    updated_at      TIMESTAMP NOT NULL,
    PRIMARY KEY (run_id) NOT ENFORCED
);

CREATE TABLE IF NOT EXISTS feature_store.backfill_partitions (
    run_id          STRING    NOT NULL,
    feature_view    STRING    NOT NULL,
    partition_date  DATE      NOT NULL,
    status          STRING    NOT NULL,
    rows_written    INT64     DEFAULT 0,
    completed_at    TIMESTAMP,
    -- idempotency: a (feature_view, partition_date) is computed at most once per success
    PRIMARY KEY (run_id, partition_date) NOT ENFORCED
);

-- Resume query: partitions not yet completed for a feature view.
-- SELECT partition_date FROM UNNEST(GENERATE_DATE_ARRAY(@start, @end)) partition_date
-- WHERE partition_date NOT IN (
--   SELECT partition_date FROM feature_store.backfill_partitions
--   WHERE feature_view = @fv AND status = 'completed');
