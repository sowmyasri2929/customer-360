"""Load the generated warehouse files using the installed MySQL command-line client."""

import argparse
import os
import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def main() -> None:
    parser = argparse.ArgumentParser(description="Create and load the RetailPulse MySQL warehouse")
    parser.add_argument("--host", default=os.environ.get("MYSQL_HOST", "localhost"))
    parser.add_argument("--port", default=os.environ.get("MYSQL_PORT", "3306"))
    parser.add_argument("--user", default=os.environ.get("MYSQL_USER", "root"))
    args = parser.parse_args()

    mysql = shutil.which("mysql")
    if not mysql:
        raise SystemExit("MySQL command-line client not found. Install MySQL, then rerun this loader.")
    command = [mysql, "--local-infile=1", "-h", args.host, "-P", str(args.port), "-u", args.user]
    for sql_file in [ROOT / "sql" / "01_schema.sql", ROOT / "sql" / "02_load_data.sql"]:
        if not sql_file.exists():
            raise SystemExit(f"Missing {sql_file}. Run python run_all.py first.")
        print(f"Executing {sql_file.name}...")
        with sql_file.open("rb") as handle:
            subprocess.run(command, stdin=handle, check=True)
    print("RetailPulse MySQL warehouse loaded successfully.")


if __name__ == "__main__":
    main()

