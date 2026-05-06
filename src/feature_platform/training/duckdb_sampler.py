"""DuckDB-based sampling for very large training joins.

Strategy from the playbook: when an offline join is huge, validate the join on a
deterministic sample with DuckDB first (seconds), then run the full warehouse job.
This catches cardinality blow-ups and key mismatches cheaply.
"""

from __future__ import annotations

import duckdb
import pandas as pd

from feature_platform.common.logging import get_logger

log = get_logger(__name__)


def sample_entities(entity_df: pd.DataFrame, fraction: float = 0.01, seed: int = 42) -> pd.DataFrame:
    """Deterministic fractional sample of entity rows."""
    if not 0 < fraction <= 1:
        raise ValueError("fraction must be in (0, 1]")
    con = duckdb.connect()
    con.register("entities", entity_df)
    sampled = con.execute(
        f"SELECT * FROM entities USING SAMPLE {fraction * 100} PERCENT (bernoulli, {seed})"
    ).df()
    log.info("sampler.sampled", n_in=len(entity_df), n_out=len(sampled), fraction=fraction)
    return sampled


def estimate_join_cardinality(entity_df: pd.DataFrame, feature_df: pd.DataFrame) -> float:
    """Rough fan-out estimate (features per entity) to catch accidental blow-ups."""
    if entity_df.empty:
        return 0.0
    con = duckdb.connect()
    con.register("e", entity_df)
    con.register("f", feature_df)
    row = con.execute(
        "SELECT CAST(COUNT(*) AS DOUBLE) / (SELECT COUNT(DISTINCT entity_id) FROM e) "
        "FROM f WHERE f.entity_id IN (SELECT entity_id FROM e)"
    ).fetchone()
    return float(row[0]) if row and row[0] is not None else 0.0
