import os
import sys
import json
from datetime import datetime, timezone, date
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app import create_app, db
from app.models.district import District
from app.models.college import College
from app.models.course import Course
from app.models.facility import Facility
from app.models.dataset_metadata import DatasetMetadata
from seed.seed_data import MANDATORY_TN_DISTRICTS

CLEAN_DATA_FILE = BASE_DIR / "data" / "validated" / "colleges_clean.json"

def import_clean_dataset():
    app = create_app('development')
    with app.app_context():
        print("Starting 100% idempotent import into EduVerse AI database...")

        # 1. Ensure all 38 districts exist
        for d_name in MANDATORY_TN_DISTRICTS:
            dist = District.query.filter_by(name=d_name).first()
            if not dist:
                dist = District(name=d_name, state='Tamil Nadu')
                db.session.add(dist)
        db.session.commit()
        print(f"[OK] Verified all 38 Tamil Nadu districts.")

        # Cache districts by id and canonical name
        district_by_name = {d.name.lower(): d for d in District.query.all()}

        # 2. Read validated clean dataset
        with open(CLEAN_DATA_FILE, 'r', encoding='utf-8') as f:
            colleges_data = json.load(f)

        print(f"Importing {len(colleges_data)} validated college records...")

        # Preload existing colleges by (normalized_name, district_id) and code
        existing_colleges = College.query.all()
        college_map = {}
        for c in existing_colleges:
            if c.normalized_name and c.district_id:
                college_map[(c.normalized_name, c.district_id)] = c
            if c.code:
                college_map[c.code] = c

        created_colleges = 0
        updated_colleges = 0
        total_courses_count = 0
        total_facilities_count = 0

        # Batch commit for performance
        batch_size = 100

        for idx, item in enumerate(colleges_data):
            norm_name = item['normalized_name']
            dist_id = item['district_id']
            code = item.get('code')

            existing = college_map.get((norm_name, dist_id)) or (college_map.get(code) if code else None)

            if existing:
                col = existing
                updated_colleges += 1
            else:
                col = College()
                created_colleges += 1
                db.session.add(col)

            # Assign properties
            col.name = item['name']
            col.normalized_name = norm_name
            col.code = code
            col.state = item.get('state', 'Tamil Nadu')
            col.district_id = dist_id
            col.district = item['district']
            col.city = item['city']
            col.college_type = item['college_type']
            col.primary_college_type = item['primary_college_type']
            col.autonomous_status = item['autonomous_status']
            col.address = item.get('address')
            col.latitude = item.get('latitude')
            col.longitude = item.get('longitude')
            col.website = item.get('website')
            col.description = item.get('description')
            col.source_url = item.get('source_url')
            col.source_name = item.get('source_name')
            col.source_type = item.get('source_type', 'OFFICIAL')
            col.source_classification = item.get('source_classification')
            col.classification_source = item.get('classification_source')
            col.data_status = item.get('data_status', 'VERIFIED')
            col.last_verified = date(2026, 9, 22)
            col.last_updated = datetime.now(timezone.utc)

            # Flush to get college id if new
            db.session.flush()

            # Update cache
            college_map[(norm_name, dist_id)] = col
            if code:
                college_map[code] = col

            # Upsert Courses
            existing_courses = {crs.course_name.lower(): crs for crs in col.courses}
            for crs_data in item.get('courses', []):
                crs_key = crs_data['course_name'].lower()
                if crs_key in existing_courses:
                    crs_obj = existing_courses[crs_key]
                else:
                    crs_obj = Course(college_id=col.id)
                    db.session.add(crs_obj)
                crs_obj.course_name = crs_data['course_name']
                crs_obj.course_category = crs_data.get('course_category')
                crs_obj.duration_years = crs_data.get('duration_years')
                crs_obj.annual_fee = crs_data.get('annual_fee')  # strictly None if not available
                crs_obj.eligibility = crs_data.get('eligibility')
                total_courses_count += 1

            # Upsert Facilities
            existing_facilities = {fac.facility_name.lower(): fac for fac in col.facilities}
            for fac_name in item.get('facilities', []):
                fac_key = fac_name.lower()
                if fac_key not in existing_facilities:
                    fac_obj = Facility(college_id=col.id, facility_name=fac_name)
                    db.session.add(fac_obj)
                total_facilities_count += 1

            if (idx + 1) % batch_size == 0:
                db.session.commit()
                print(f"Processed {idx + 1}/{len(colleges_data)} colleges...")

        db.session.commit()

        # 3. Insert or update dataset metadata
        meta = DatasetMetadata.query.filter_by(dataset_version="1.0.0").first()
        if not meta:
            meta = DatasetMetadata(dataset_version="1.0.0")
            db.session.add(meta)

        meta.source = "Comprehensive Directory of 1000 Higher Education Institutions in Tamil Nadu + DCE/DOTE Official Gazette"
        meta.retrieved_at = datetime.now(timezone.utc)
        meta.total_records = College.query.count()
        meta.verified_records = College.query.filter_by(data_status='VERIFIED').count()
        meta.notes = (
            f"Idempotent import completed on 2026-09-25. "
            f"Total unique colleges: {meta.total_records}. "
            f"All 38 districts supported."
        )
        db.session.commit()

        print("\n==========================================")
        print("IMPORT COMPLETED SUCCESSFULLY")
        print("==========================================")
        print(f"Colleges created: {created_colleges}")
        print(f"Colleges updated: {updated_colleges}")
        print(f"Total Colleges in DB: {College.query.count()}")
        print(f"Total Courses in DB: {Course.query.count()}")
        print(f"Total Facilities in DB: {Facility.query.count()}")
        print(f"DatasetMetadata record updated.")
        print("==========================================")

if __name__ == '__main__':
    import_clean_dataset()
