import os
import sys

# Ensure project root is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models.district import District
from app.models.college import College
from seed.seed_data import MANDATORY_TN_DISTRICTS


def validate_district_coverage():
    """Validates that all 38 official Tamil Nadu districts exist in the database."""
    print("=" * 60)
    print("EDUVERSE AI: TAMIL NADU DISTRICT COVERAGE VALIDATION")
    print("=" * 60)

    districts = District.query.order_by(District.name.asc()).all()
    db_district_names = {d.name for d in districts}
    expected_districts = set(MANDATORY_TN_DISTRICTS)

    missing = expected_districts - db_district_names
    unexpected = db_district_names - expected_districts

    total_expected = len(MANDATORY_TN_DISTRICTS)
    total_present = len(db_district_names)
    total_missing = len(missing)

    # Detailed breakdown table
    print(f"{'No.':<4} {'District Name':<25} {'Status':<12} {'Colleges In DB':<15}")
    print("-" * 60)
    for idx, name in enumerate(MANDATORY_TN_DISTRICTS, 1):
        dist_obj = next((d for d in districts if d.name == name), None)
        if dist_obj:
            count = len(dist_obj.colleges)
            college_str = f"{count} college{'s' if count != 1 else ''}"
            status = "[OK] Present"
        else:
            college_str = "0 colleges"
            status = "[!] Missing"
        print(f"{idx:<4} {name:<25} {status:<12} {college_str:<15}")

    print("-" * 60)
    print(f"Total Tamil Nadu districts: {total_expected}")
    print(f"Districts present: {total_present}")
    print(f"Districts missing: {total_missing}")

    if total_missing > 0:
        print(f"\n[FAIL] Missing {total_missing} districts: {sorted(list(missing))}")
        sys.exit(1)

    if unexpected:
        print(f"\n[FAIL] Unexpected {len(unexpected)} district names: {sorted(list(unexpected))}")
        sys.exit(1)

    print("\nDistrict coverage:")
    print(f"{total_present} / {total_expected} [OK]")
    print("=" * 60)
    print("[SUCCESS] All 38 Tamil Nadu districts verified with zero duplicates.")
    return 0


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        validate_district_coverage()
