"""
Test script to verify database insertion pipeline.
Loads data.json -> validates -> normalizes -> inserts into DB.
"""

import json
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.validation import validate_fields, normalize_json
from db.connection import get_session, init_db
from db.service import insert_company_bundle


def load_data_json(file_path: str):
    """Load and parse data.json file."""
    with open(file_path, 'r') as f:
        return json.load(f)


def main():
    """Main test workflow: JSON -> Validation -> Normalization -> Insertion."""

    print("=" * 60)
    print("DATABASE INSERTION TEST")
    print("=" * 60)

    # Step 1: Initialize database (create tables)
    print("\n[1/5] Initializing database...")
    init_db()

    # Step 2: Load data.json
    data_json_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data.json')
    print(f"\n[2/5] Loading data from {data_json_path}...")
    raw_data = load_data_json(data_json_path)
    print(f"Loaded {len(raw_data)} company objects from JSON")

    # Step 3: Validate fields
    print("\n[3/5] Validating fields...")
    validated_data = validate_fields(raw_data)
    print(f"Validated: {len(validated_data)} companies passed validation")

    # Step 4: Normalize to SQLAlchemy objects
    print("\n[4/5] Normalizing to SQLAlchemy models...")
    bundles = normalize_json(validated_data)
    print(f"Normalized: {len(bundles)} company bundles created")

    # Step 5: Insert into database
    print("\n[5/5] Inserting into database...")
    print("-" * 60)

    results = []
    for idx, bundle in enumerate(bundles, 1):
        print(f"\n[{idx}/{len(bundles)}] Processing: {bundle.company.cname}")

        with get_session() as session:
            try:
                result = insert_company_bundle(bundle, session)
                session.commit()  # Commit per company
                results.append(result)
                print(f"✓ Success")

            except Exception as e:
                session.rollback()
                print(f"✗ Failed: {e}")
                results.append({
                    'success': False,
                    'company_name': bundle.company.cname,
                    'error': str(e)
                })

    # Summary
    print("\n" + "=" * 60)
    print("INSERTION SUMMARY")
    print("=" * 60)

    successful = [r for r in results if r.get('success')]
    failed = [r for r in results if not r.get('success')]

    print(f"\nTotal companies processed: {len(results)}")
    print(f"Successful insertions: {len(successful)}")
    print(f"Failed insertions: {len(failed)}")

    if successful:
        total_emails = sum(r.get('emails_inserted', 0) for r in successful)
        total_recruiters = sum(r.get('recruiters_inserted', 0) for r in successful)
        total_recruiter_emails = sum(r.get('recruiter_emails_inserted', 0) for r in successful)
        total_jobs = sum(r.get('jobs_inserted', 0) for r in successful)

        print(f"\nTotal emails inserted: {total_emails}")
        print(f"Total recruiters inserted: {total_recruiters}")
        print(f"Total recruiter_emails inserted: {total_recruiter_emails}")
        print(f"Total jobs inserted: {total_jobs}")

    if failed:
        print("\nFailed companies:")
        for r in failed:
            print(f"  - {r.get('company_name')}: {r.get('error')}")

    print("\n" + "=" * 60)
    print("Test complete!")
    print("=" * 60)


if __name__ == '__main__':
    main()
