from datetime import datetime
from airflow import DAG
from airflow.operators.python import PythonOperator


# ✅ SAFE WRAPPERS (VERY IMPORTANT)

def run_ingestion_safe():
    from ingestion.fetch_stock_data import run_ingestion
    run_ingestion()


def run_feature_pipeline_all():
    from processing.feature_engineering import run_feature_pipeline
    from config.config import STOCK_SYMBOLS

    for symbol in STOCK_SYMBOLS:
        run_feature_pipeline(symbol)


def run_training_safe():
    from models.train_model import main
    main()


def run_prediction_safe():
    from models.predict import main
    main()


# ✅ DEFAULT ARGS
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "retries": 1,
}


# ✅ DAG DEFINITION
dag = DAG(
    dag_id="stock_pipeline_dag",
    default_args=default_args,
    start_date=datetime(2024, 1, 1),
    schedule="@daily",   # ✅ updated (no warning)
    catchup=False,
)


# ✅ TASKS
ingestion_task = PythonOperator(
    task_id="fetch_stock_data",
    python_callable=run_ingestion_safe,
    dag=dag,
)

feature_task = PythonOperator(
    task_id="feature_engineering",
    python_callable=run_feature_pipeline_all,
    dag=dag,
)

training_task = PythonOperator(
    task_id="train_model",
    python_callable=run_training_safe,
    dag=dag,
)

prediction_task = PythonOperator(
    task_id="predict_stock",
    python_callable=run_prediction_safe,
    dag=dag,
)


# ✅ DEPENDENCIES
ingestion_task >> feature_task >> training_task >> prediction_task