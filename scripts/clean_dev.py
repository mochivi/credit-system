#!/usr/bin/env python3
import os
import sys
import argparse
from sqlalchemy import create_engine, text

# Tables ordered to satisfy FK constraints (children first)
TABLES_IN_DELETE_ORDER = [
    "emotional_events",
    "transactions",
    "credit_offers",
    "credit_accounts",
    "risk_assessments",
    "users",
    "clients",
]

def clean(db_url: str) -> None:
    engine = create_engine(db_url)
    with engine.begin() as conn:
        # Temporarily defer/disable constraints for the session
        conn.execute(text("SET session_replication_role = 'replica'"))
        try:
            for table in TABLES_IN_DELETE_ORDER:
                conn.execute(text(f"DELETE FROM {table}"))
        finally:
            conn.execute(text("SET session_replication_role = 'origin'"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Delete dev data from all ECS tables")
    parser.add_argument("--yes", action="store_true", help="Run without interactive prompt")
    parser.add_argument("--wipe-clients", action="store_true", help="Also wipe API clients table")
    args = parser.parse_args()

    if not args.yes:
        print("Refusing to clean: pass --yes to proceed")
        return 0

    db_url = os.getenv("DB_URL", "")
    if not db_url:
        print("ERROR: DB_URL env var is required")
        return 2

    try:
        clean(db_url)
        print("Clean completed.")
        return 0
    except Exception as exc:
        print(f"ERROR: cleaning failed: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
