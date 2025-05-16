import csv
import os

results_folder_path = "results/methods"

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
    "6th run (ms)",
    "7th run (ms)",
    "8th run (ms)",
    "9th run (ms)",
    "10th run (ms)",
    "Average (ms)",
    "Performance improvement (%)"
]

def get_filename(method_id: int) -> str:
    return f"{results_folder_path}/method_{method_id}.csv"

def write_result(method_id: int, results):
    results_path = get_filename(method_id)
    file_exists = os.path.isfile(results_path)
    is_empty = not file_exists or os.path.getsize(results_path) == 0

    with open(results_path, "a", newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if is_empty:
            writer.writeheader()

        writer.writerows(results)

def is_method_result_present(method_id: int) -> bool:
    results_path = get_filename(method_id)
    return os.path.isfile(results_path)

def sort_results_by_method_id_and_variant_id(method_id: int):
    results_path = get_filename(method_id)
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
