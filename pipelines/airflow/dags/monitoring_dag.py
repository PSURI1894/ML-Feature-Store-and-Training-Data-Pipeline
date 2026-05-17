"""Nightly monitoring DAG: drift, freshness, null-rate, training-serving skew."""

from __future__ import annotations

from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator


def _run_drift(**_: object) -> None:
    from feature_platform.monitoring.drift import run_drift_scan

    report = run_drift_scan(all_views=True)
    if report.alerted:
        raise ValueError(f"drift detected on {sum(d.alert for d in report.drifts)} features")


def _run_skew(**_: object) -> None:
    from feature_platform.monitoring.skew import reconcile_all

    reconcile_all()


with DAG(
    dag_id="feature_monitoring",
    schedule="30 3 * * *",           # 03:30 UTC nightly
    start_date=datetime(2026, 4, 15),
    catchup=False,
    default_args={"owner": "ml-platform", "retries": 1, "retry_delay": timedelta(minutes=10)},
    tags=["features", "monitoring"],
) as dag:
    drift = PythonOperator(task_id="drift_scan", python_callable=_run_drift)
    skew = PythonOperator(task_id="skew_reconcile", python_callable=_run_skew)
    drift >> skew
