import os
import sys
from pathlib import Path
from collections import Counter

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app import create_app, db
from app.models.district import District
from app.models.college import College
from app.models.course import Course
from app.models.facility import Facility
from app.models.dataset_metadata import DatasetMetadata

def run_validation():
    app = create_app('development')
    with app.app_context():
        colleges = College.query.all()
        districts = District.query.all()
        courses = Course.query.all()
        facilities = Facility.query.all()

        total_colleges = len(colleges)
        total_districts = len(districts)

        # Unique districts with colleges
        districts_with_colleges = len(set(c.district_id for c in colleges if c.district_id))

        # Category breakdowns using controlled vocabulary
        gov_count = College.query.filter(
            (College.primary_college_type == 'GOVERNMENT') | (College.college_type == 'Government')
        ).count()

        aided_count = College.query.filter(
            (College.primary_college_type == 'GOVERNMENT_AIDED') | (College.college_type == 'Government-Aided')
        ).count()

        sf_count = College.query.filter(
            (College.primary_college_type == 'SELF_FINANCING') | (College.college_type == 'Self-Financing')
        ).count()

        autonomous_count = College.query.filter(
            (College.autonomous_status == 'AUTONOMOUS') | (College.name.ilike('%(autonomous)%'))
        ).count()

        other_count = College.query.filter(
            (College.primary_college_type == 'OTHER') | (College.college_type.in_(['University Department', 'Deemed University']))
        ).count()

        unknown_count = College.query.filter(
            College.primary_college_type == 'UNKNOWN'
        ).count()

        # Data quality checks
        verified_count = College.query.filter_by(data_status='VERIFIED').count()
        unverified_count = College.query.filter_by(data_status='UNVERIFIED').count()
        sample_count = College.query.filter_by(data_status='SAMPLE').count()

        missing_source = College.query.filter((College.source_url == None) | (College.source_url == '')).count()
        missing_district = College.query.filter(College.district_id == None).count()
        invalid_coords = sum(1 for c in colleges if (c.latitude is not None or c.longitude is not None) and not c.has_valid_coordinates)

        # Duplicate detection by (normalized_name, district_id)
        seen_keys = set()
        duplicates = 0
        for c in colleges:
            key = (c.normalized_name or c.name.lower().strip(), c.district_id)
            if key in seen_keys:
                duplicates += 1
            else:
                seen_keys.add(key)

        # Target checks
        pass_total = total_colleges >= 501
        pass_gov = gov_count >= 101
        pass_aided = aided_count >= 101
        pass_sf = sf_count >= 101
        pass_auto = autonomous_count >= 101
        pass_districts = total_districts == 38 and districts_with_colleges == 38

        print("========================================")
        print("EDUVERSE AI DATASET VALIDATION")
        print("========================================")
        print(f"\nTotal unique colleges:\n{total_colleges}")
        print(f"\nDistricts:\n{total_districts} / 38")
        print(f"\nDistricts with college records:\n{districts_with_colleges} / 38")
        print(f"\nGovernment:\n{gov_count}")
        print(f"\nGovernment-Aided:\n{aided_count}")
        print(f"\nSelf-Financing:\n{sf_count}")
        print(f"\nAutonomous:\n{autonomous_count}")
        print(f"\nOther:\n{other_count}")
        print(f"\nUnknown:\n{unknown_count}")
        print(f"\nCourses:\n{len(courses)}")
        print(f"\nFacilities:\n{len(facilities)}")
        print(f"\nVerified records:\n{verified_count}")
        print(f"\nUnverified records:\n{unverified_count}")
        print(f"\nSample records:\n{sample_count}")
        print(f"\nMissing source:\n{missing_source}")
        print(f"\nDuplicate candidates:\n{duplicates}")
        print(f"\nMissing district:\n{missing_district}")
        print(f"\nInvalid coordinates:\n{invalid_coords}")
        print("\n========================================")
        print("TARGET STATUS")
        print("========================================")
        print(f"\nTotal colleges >= 501:\n{'PASS' if pass_total else 'FAIL'}")
        print(f"\nGovernment >= 101:\n{'PASS' if pass_gov else 'FAIL'}")
        print(f"\nGovernment-Aided >= 101:\n{'PASS' if pass_aided else 'FAIL'}")
        print(f"\nSelf-Financing >= 101:\n{'PASS' if pass_sf else 'FAIL'}")
        print(f"\nAutonomous >= 101:\n{'PASS' if pass_auto else 'FAIL'}")
        print(f"\n38 District Coverage:\n{'PASS' if pass_districts else 'FAIL'}")
        print("========================================\n")

if __name__ == '__main__':
    run_validation()
