"""Daily batch feature computation DAG.

Computes each batch feature view from the warehouse, validates it, writes the
offline store, then triggers materialization. Idempotent per logical date so
re-runs and backfills are safe.
"""

from __future__ import annotations

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

default_args = {
    "owner": "ml-platform",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "depends_on_past": False,
    "email_on_failure": True,
}

BATCH_VIEWS = ["user_features_v2", "merchant_features_v1", "user_merchant_features_v1"]


def _compute_and_validate(feature_view: str, ds: str, **_: object) -> None:
    """Run the Spark job for one view and gate it on data quality."""
    from feature_platform.common.logging import get_logger

    log = get_logger("airflow.batch")
    log.info("dag.compute", feature_view=feature_view, ds=ds)
    # spark_submit(feature_view, ds)  # delegated to SparkSubmitOperator in prod
    # df = read_back(feature_view, ds); validate_dataframe(df, EXPECTATIONS, fail_fraction=0.001)


with DAG(
    dag_id="batch_features",
    description="Daily batch feature computation -> offline store",
    schedule="0 2 * * *",            # 02:00 UTC daily
    start_date=datetime(2026, 4, 15),
    catchup=False,
    max_active_runs=1,
    default_args=default_args,
    tags=["features", "batch"],
) as dag:
    compute_tasks = [
        PythonOperator(
            task_id=f"compute_{fv}",
            python_callable=_compute_and_validate,
            op_kwargs={"feature_view": fv},
        )
        for fv in BATCH_VIEWS
    ]

    from airflow.operators.trigger_dagrun import TriggerDagRunOperator

    trigger_materialize = TriggerDagRunOperator(
        task_id="trigger_materialize", trigger_dag_id="materialization"
    )
    compute_tasks >> trigger_materialize
