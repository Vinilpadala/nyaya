import sqlite3
import csv
import os

def export_database():
    db_path = os.path.join(os.path.dirname(__file__), "nyaya-api", "nyaya.db")
    output_dir = os.path.join(os.path.dirname(__file__), "database")
    os.makedirs(output_dir, exist_ok=True)

    print(f"Reading SQLite Database from: {db_path}")
    print(f"Exporting CSV files to: {output_dir}\n")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall() if not row[0].startswith("sqlite_")]

    exported_files = []
    for table in tables:
        cursor.execute(f'SELECT * FROM "{table}"')
        rows = cursor.fetchall()
        headers = [desc[0] for desc in cursor.description]

        csv_filename = f"{table}.csv"
        csv_filepath = os.path.join(output_dir, csv_filename)

        with open(csv_filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)

        print(f"  [OK] Exported {len(rows)} rows -> database/{csv_filename}")

        exported_files.append(csv_filename)

    conn.close()
    print("\nDatabase CSV export completed successfully!")
    return exported_files

if __name__ == "__main__":
    export_database()
