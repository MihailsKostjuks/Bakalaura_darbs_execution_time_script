import json
import os
import psycopg2
from dotenv import load_dotenv
from utils.file_operations import read_existing_results, write_result, sort_results_by_method_id_and_variant_id

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

def execute_scripts(
        dbname: str,
        query: str,
        is_testable_query: bool = False
) -> float:
    execution_time = None
    # start_postgresql_service()
    connection = psycopg2.connect(
        dbname=dbname,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    cursor = connection.cursor()
    if is_testable_query:
        connection.autocommit = True
        cursor = connection.cursor()
        try:
            cursor.execute("DISCARD ALL")
        except Exception as e:
            print(f"DISCARD ALL failed: {e}")
        connection.autocommit = False
    else:
        cursor = connection.cursor()

    if is_testable_query:
        cursor.execute("EXPLAIN ANALYZE " + query)
    else:
        cursor.execute(query)

    if is_testable_query:
        explain_result = cursor.fetchall()
        for row in explain_result:
            if len(row) and 'Execution Time' in row[0]:
                execution_time_complete_string = row[0]
                parts = execution_time_complete_string.split('Execution Time: ')
                time_value_and_metric = parts[1]
                time_value_ms = time_value_and_metric.split()[0]
                execution_time = float(time_value_ms)

    connection.commit()
    return execution_time



def process_methods():
    with open("methods.json", 'r') as f:
        methods = json.load(f)

    existing_results = read_existing_results()
    for method in methods:
        method_id = method.get("method_id")
        if str(method_id) in existing_results:
            print(f"Skipping method {method_id}: already in  CSV results")
            continue
        if method_id != 0: # 0 is a placeholder for upcoming methods
            for method_data_id, method_data in enumerate(method.get("method_data", []), start=1):

                db_name = method_data.get("database_name")
                for variation_index, variation in enumerate(method_data.get("baseline_and_variations", []), start=1):

                    durations = []

                    for script in variation.get("setup_scripts", []):
                        execute_scripts(db_name, script)

                    query_script = variation.get("query_script")
                    for _ in range(5):
                        # stop_postgresql_service()
                        duration = execute_scripts(db_name, query_script, is_testable_query=True)
                        durations.append(duration)

                    for script in variation.get("cleanup_scripts", []):
                        execute_scripts(db_name, script)

                    variant = "Baseline" if variation_index == 1 else "Solution " + str(variation_index-1)
                    dataset_type = "original" if method_data_id == 1 else "reproduced"

                    durations = [round(d, 2) for d in durations]
                    average_duration = round(sum(durations) / len(durations), 2)

                    variant_result = {
                        "Method id": method_id,
                        "Database name": db_name,
                        "Dataset type": dataset_type,
                        "Variant id": variation_index,
                        "Variant": variant,
                        "Executed query": query_script,
                        "1st run (ms)": durations[0],
                        "2nd run (ms)": durations[1],
                        "3rd run (ms)": durations[2],
                        "4th run (ms)": durations[3],
                        "5th run (ms)": durations[4],
                        "Average (ms)": average_duration
                    }

                    write_result([variant_result])

    sort_results_by_method_id_and_variant_id()


if __name__ == "__main__":
    process_methods()