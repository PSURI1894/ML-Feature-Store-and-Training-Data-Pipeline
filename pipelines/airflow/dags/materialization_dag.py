"""Materialization DAG: copy recent offline values to the online store.

Scheduled more frequently than batch compute, and additionally tied to traffic
patterns (pre-warm before known peaks) — see fix/online-ttl-expiry-peak.
"""

from __future__ import annotations

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator


def _materialize(**_: object) -> None:
    from feature_platform.common.time_utils import utcnow
    from feature_platform.batch.runner import materialize_recent

    end = utcnow()
    materialize_recent(start=end - timedelta(days=1), end=end)


with DAG(
    dag_id="materialization",
    description="Materialize offline -> online with TTL",
    schedule="0 */4 * * *",          # every 4 hours
    start_date=datetime(2026, 4, 15),
    catchup=False,
    max_active_runs=1,
    default_args={"owner": "ml-platform", "retries": 3, "retry_delay": timedelta(minutes=2)},
    tags=["features", "materialize"],
) as dag:
    PythonOperator(task_id="materialize_all", python_callable=_materialize)
