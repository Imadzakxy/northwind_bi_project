import argparse
from extract import main as extract_main
from transform import main as transform_data
from load import main as load_to_sqlite


def run_pipeline(source='excel', db_conn_string=None):
    print("\n=== STEP 1 — EXTRACT ===")
    extract_main(source=source, db_conn_string=db_conn_string)

    print("\n=== STEP 2 — TRANSFORM ===")
    transform_data()

    print("\n=== STEP 3 — LOAD ===")
    load_to_sqlite()

    print("[✔] ETL Pipeline finished successfully!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run full ETL pipeline (choose source)')
    parser.add_argument('--source', choices=['excel','sql'], default='excel', help="Source des données: 'excel' or 'sql'")
    parser.add_argument('--db-conn', dest='db_conn', default=None, help='SQLAlchemy connection string when using --source sql')
    args = parser.parse_args()

    run_pipeline(source=args.source, db_conn_string=args.db_conn)
