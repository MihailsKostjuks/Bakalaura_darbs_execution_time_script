import csv
import os

results_path = "results/benchmark_results.csv"

fieldnames = [
    "Method id",
    "Database name",
    "Dataset type",
    "Variant id",
    "Variant",
    "Executed query",
    "1st run (ms)",
    "2nd run (ms)",
    "3rd run (ms)",
    "4th run (ms)",
    "5th run (ms)",
    "Average (ms)"
]

def write_result(results):
    file_exists = os.path.isfile(results_path)
    is_empty = not file_exists or os.path.getsize(results_path) == 0

    with open(results_path, "a", newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if is_empty:
            writer.writeheader()

        writer.writerows(results)

def read_existing_results():
    existing = set()
    try:
        with open(results_path, "r", newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                method_id = row["Method id"]
                existing.add(method_id)
    except Exception as e:
        pass
    return existing

def sort_results_by_method_id_and_variant_id():
    if not os.path.isfile(results_path):
        print(f"File {results_path} does not exist")
        return

    with open(results_path, "r", newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        rows = list(reader)

    dataset_sort_priority = {"original": 0, "reproduced": 1}

    # sorting by:
    # 1. method id
    # 2. dataset (putting original 1st, reproduced later)
    # 3. database
    # 4. variant id (Baseline first, Solution 1/2 ... later)
    sorted_rows = sorted(
        rows,
        key=lambda row: (
            int(row["Method id"]),
            dataset_sort_priority.get(row.get("Dataset type", "reproduced")),
            row["Database name"].lower(),
            int(row.get("Variant id", 0))
        )
    )

    with open(results_path, "w", newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(sorted_rows)
