#!/usr/bin/env python3
"""
EduVerse AI - SQLite to PostgreSQL Migration Script
====================================================
Safely migrates all data from local SQLite to the Antideploy PostgreSQL database.
- Preserves all hashed passwords
- Preserves all student records privately
- Verifies row counts against source before declaring success
- Never truncates or resets existing data

Usage:
    python scripts/migrate_sqlite_to_postgres.py

Requires:
    DATABASE_URL env var pointing to PostgreSQL (set from .env or Antideploy)
    Source SQLite at ./eduverse_dev.db or ./instance/eduverse_dev.db
"""

import os
import sys
import sqlite3
from pathlib import Path
from datetime import datetime

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Load .env
from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / '.env')

DATABASE_URL = os.getenv('DATABASE_URL', '')
if not DATABASE_URL or 'sqlite' in DATABASE_URL.lower():
    print("ERROR: DATABASE_URL must point to a PostgreSQL database.")
    print(f"  Current value: {DATABASE_URL[:40]}..." if DATABASE_URL else "  Not set.")
    sys.exit(1)

# Fix postgres:// -> postgresql:// for SQLAlchemy
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    os.environ['DATABASE_URL'] = DATABASE_URL

# Find SQLite source
SQLITE_CANDIDATES = [
    PROJECT_ROOT / 'eduverse_dev.db',
    PROJECT_ROOT / 'instance' / 'eduverse_dev.db',
]
SQLITE_PATH = None
for candidate in SQLITE_CANDIDATES:
    if candidate.exists():
        SQLITE_PATH = candidate
        break

if not SQLITE_PATH:
    print("ERROR: Could not find local SQLite database. Checked:")
    for c in SQLITE_CANDIDATES:
        print(f"  {c}")
    sys.exit(1)

print(f"\n{'='*65}")
print("  EduVerse AI - Data Migration: SQLite → PostgreSQL")
print(f"{'='*65}")
print(f"  Source  : {SQLITE_PATH}")
print(f"  Target  : {DATABASE_URL[:40]}...")
print(f"{'='*65}\n")

# Connect to SQLite source
src_conn = sqlite3.connect(str(SQLITE_PATH))
src_conn.row_factory = sqlite3.Row
src_cur = src_conn.cursor()

# Get all tables and counts from source
src_cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name != 'alembic_version'")
tables = [row[0] for row in src_cur.fetchall()]

source_counts = {}
for table in tables:
    src_cur.execute(f"SELECT COUNT(*) FROM [{table}]")
    source_counts[table] = src_cur.fetchone()[0]

print("Source row counts:")
for t, c in source_counts.items():
    print(f"  {t}: {c}")
print()

# Connect Flask app to PostgreSQL and run migrations
from app import create_app, db
from app.models import (
    User, District, College, Course, Facility, StudentPreference,
    ComparisonItem, DatasetMetadata, StudentQuery, StudentLoginActivity,
    StudentFeedback, StudentProfile
)

app = create_app('production')

with app.app_context():
    print("Running Flask-Migrate (flask db upgrade) against PostgreSQL...")
    from flask_migrate import upgrade
    upgrade()
    print("  ✓ Schema applied to PostgreSQL\n")

    # --- Helper ---
    def migrate_table(table_name, model_class, transform=None):
        """Read all rows from SQLite, insert into PostgreSQL (skip existing by PK)."""
        src_cur.execute(f"SELECT * FROM [{table_name}]")
        rows = src_cur.fetchall()
        if not rows:
            print(f"  {table_name}: 0 rows in source, skipping.")
            return 0

        columns = [desc[0] for desc in src_cur.description]
        inserted = 0
        skipped = 0

        for row in rows:
            data = dict(zip(columns, row))
            if transform:
                data = transform(data)
            if data is None:
                skipped += 1
                continue

            # Check if record already exists (by primary key)
            existing = db.session.get(model_class, data.get('id'))
            if existing:
                skipped += 1
                continue

            try:
                obj = model_class(**data)
                db.session.add(obj)
                db.session.flush()
                inserted += 1
            except Exception as e:
                db.session.rollback()
                print(f"    WARNING: Could not insert row id={data.get('id')}: {e}")
                skipped += 1

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"    ERROR committing {table_name}: {e}")
            return inserted

        return inserted

    def parse_dt(val):
        """Parse datetime strings from SQLite."""
        if not val:
            return None
        if isinstance(val, datetime):
            return val
        for fmt in ('%Y-%m-%d %H:%M:%S.%f', '%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S.%f', '%Y-%m-%dT%H:%M:%S'):
            try:
                return datetime.strptime(val, fmt)
            except (ValueError, TypeError):
                pass
        return None

    def parse_date(val):
        if not val:
            return None
        try:
            return datetime.strptime(val, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            return None

    migration_results = {}

    # 1. Districts
    print("Migrating districts...")
    def transform_district(d):
        return {
            'id': d['id'],
            'name': d['name'],
            'state': d.get('state', 'Tamil Nadu'),
        }
    migration_results['districts'] = migrate_table('districts', District, transform_district)
    print(f"  ✓ districts: {migration_results['districts']} inserted")

    # 2. Users (passwords already hashed)
    print("Migrating users (passwords remain hashed)...")
    def transform_user(u):
        return {
            'id': u['id'],
            'name': u['name'],
            'email': u['email'],
            'password_hash': u['password_hash'],
            'role': u.get('role', 'student'),
            'last_login_at': parse_dt(u.get('last_login_at')),
            'last_activity_at': parse_dt(u.get('last_activity_at')),
            'created_at': parse_dt(u.get('created_at')) or datetime.utcnow(),
        }
    migration_results['users'] = migrate_table('users', User, transform_user)
    print(f"  ✓ users: {migration_results['users']} inserted")

    # 3. Colleges
    print("Migrating colleges (1129 records)...")
    def transform_college(c):
        return {
            'id': c['id'],
            'name': c['name'],
            'code': c.get('code'),
            'state': c.get('state', 'Tamil Nadu'),
            'district_id': c.get('district_id'),
            'district': c.get('district', ''),
            'city': c.get('city', ''),
            'college_type': c.get('college_type', ''),
            'primary_college_type': c.get('primary_college_type', 'UNKNOWN'),
            'autonomous_status': c.get('autonomous_status', 'NON_AUTONOMOUS'),
            'normalized_name': c.get('normalized_name'),
            'source_name': c.get('source_name'),
            'source_type': c.get('source_type', 'OFFICIAL'),
            'source_classification': c.get('source_classification'),
            'classification_source': c.get('classification_source'),
            'last_verified': parse_date(c.get('last_verified')),
            'address': c.get('address'),
            'latitude': c.get('latitude'),
            'longitude': c.get('longitude'),
            'website': c.get('website'),
            'official_website': c.get('official_website'),
            'official_website_url': c.get('official_website_url'),
            'website_status': c.get('website_status', 'UNVERIFIED'),
            'phone': c.get('phone'),
            'email': c.get('email'),
            'accreditation': c.get('accreditation'),
            'affiliation': c.get('affiliation'),
            'rating': c.get('rating'),
            'placement_info': c.get('placement_info'),
            'description': c.get('description'),
            'source_url': c.get('source_url'),
            'data_status': c.get('data_status', 'SAMPLE'),
            'last_updated': parse_dt(c.get('last_updated')) or datetime.utcnow(),
            'created_at': parse_dt(c.get('created_at')) or datetime.utcnow(),
        }
    migration_results['colleges'] = migrate_table('colleges', College, transform_college)
    print(f"  ✓ colleges: {migration_results['colleges']} inserted")

    # 4. Courses
    print("Migrating courses (8120 records)...")
    from app.models.course import Course as CourseModel
    src_cur.execute("SELECT * FROM courses")
    course_rows = src_cur.fetchall()
    course_cols = [d[0] for d in src_cur.description]
    course_inserted = 0
    BATCH_SIZE = 500
    batch = []
    for row in course_rows:
        data = dict(zip(course_cols, row))
        existing = db.session.get(CourseModel, data.get('id'))
        if existing:
            continue
        batch.append(CourseModel(
            id=data['id'],
            college_id=data['college_id'],
            course_name=data.get('course_name', ''),
            course_category=data.get('course_category'),
            degree=data.get('degree'),
            department=data.get('department'),
            annual_fee=data.get('annual_fee'),
            duration_years=data.get('duration_years'),
            intake_seats=data.get('intake_seats') or data.get('intake'),
            admission_mode=data.get('admission_mode'),
            eligibility=data.get('eligibility'),
            created_at=parse_dt(data.get('created_at')) or datetime.utcnow(),
        ))
        if len(batch) >= BATCH_SIZE:
            db.session.add_all(batch)
            try:
                db.session.commit()
                course_inserted += len(batch)
            except Exception as e:
                db.session.rollback()
                print(f"    WARNING: Batch commit error: {e}")
            batch = []
    if batch:
        db.session.add_all(batch)
        try:
            db.session.commit()
            course_inserted += len(batch)
        except Exception as e:
            db.session.rollback()
            print(f"    WARNING: Final batch error: {e}")
    migration_results['courses'] = course_inserted
    print(f"  ✓ courses: {course_inserted} inserted")

    # 5. Facilities
    print("Migrating facilities (7938 records)...")
    from app.models.facility import Facility as FacilityModel
    src_cur.execute("SELECT * FROM facilities")
    fac_rows = src_cur.fetchall()
    fac_cols = [d[0] for d in src_cur.description]
    fac_inserted = 0
    batch = []
    for row in fac_rows:
        data = dict(zip(fac_cols, row))
        existing = db.session.get(FacilityModel, data.get('id'))
        if existing:
            continue
        batch.append(FacilityModel(
            id=data['id'],
            college_id=data['college_id'],
            facility_name=data.get('facility_name', ''),
        ))
        if len(batch) >= BATCH_SIZE:
            db.session.add_all(batch)
            try:
                db.session.commit()
                fac_inserted += len(batch)
            except Exception as e:
                db.session.rollback()
                print(f"    WARNING: Batch commit error: {e}")
            batch = []
    if batch:
        db.session.add_all(batch)
        try:
            db.session.commit()
            fac_inserted += len(batch)
        except Exception as e:
            db.session.rollback()
    migration_results['facilities'] = fac_inserted
    print(f"  ✓ facilities: {fac_inserted} inserted")

    # 6. Student Preferences
    print("Migrating student_preferences...")
    from app.models.preference import StudentPreference as SPModel
    def transform_pref(p):
        return {
            'id': p['id'],
            'user_id': p.get('user_id'),
            'course_name': p.get('course_name'),
            'state': p.get('state', 'Tamil Nadu'),
            'district': p.get('district'),
            'city': p.get('city'),
            'budget': p.get('budget'),
            'college_type': p.get('college_type'),
            'facility_preferences': p.get('facility_preferences'),
            'placement_preference': p.get('placement_preference'),
            'created_at': parse_dt(p.get('created_at')) or datetime.utcnow(),
        }
    migration_results['student_preferences'] = migrate_table('student_preferences', SPModel, transform_pref)
    print(f"  ✓ student_preferences: {migration_results['student_preferences']} inserted")

    # 7. Comparison Items
    print("Migrating comparison_items...")
    from app.models.comparison import ComparisonItem as CIModel
    def transform_ci(c):
        return {
            'id': c['id'],
            'session_key': c.get('session_key'),
            'user_id': c.get('user_id'),
            'college_id': c['college_id'],
            'created_at': parse_dt(c.get('created_at')) or datetime.utcnow(),
        }
    migration_results['comparison_items'] = migrate_table('comparison_items', CIModel, transform_ci)
    print(f"  ✓ comparison_items: {migration_results['comparison_items']} inserted")

    # 8. Dataset Metadata
    print("Migrating dataset_metadata...")
    from app.models.dataset_metadata import DatasetMetadata as DMModel
    def transform_dm(d):
        return {
            'id': d['id'],
            'dataset_name': d.get('dataset_name', ''),
            'source': d.get('source'),
            'record_count': d.get('record_count'),
            'last_updated': parse_dt(d.get('last_updated')) or datetime.utcnow(),
            'notes': d.get('notes'),
        }
    migration_results['dataset_metadata'] = migrate_table('dataset_metadata', DMModel, transform_dm)
    print(f"  ✓ dataset_metadata: {migration_results['dataset_metadata']} inserted")

    # 9. Student Profiles
    print("Migrating student_profiles (private)...")
    from app.models.student_profile import StudentProfile as SProfModel
    src_cur.execute("SELECT * FROM student_profiles")
    prof_rows = src_cur.fetchall()
    if prof_rows:
        prof_cols = [d[0] for d in src_cur.description]
        prof_inserted = 0
        for row in prof_rows:
            data = dict(zip(prof_cols, row))
            existing = db.session.get(SProfModel, data.get('id'))
            if existing:
                continue
            # Build kwargs dynamically from columns present
            kwargs = {k: v for k, v in data.items() if hasattr(SProfModel, k)}
            # Fix datetime fields
            for dt_field in ['created_at', 'updated_at', 'date_of_birth']:
                if dt_field in kwargs:
                    kwargs[dt_field] = parse_dt(kwargs[dt_field])
            try:
                obj = SProfModel(**kwargs)
                db.session.add(obj)
                db.session.commit()
                prof_inserted += 1
            except Exception as e:
                db.session.rollback()
                print(f"    WARNING profile id={data.get('id')}: {e}")
        migration_results['student_profiles'] = prof_inserted
    else:
        migration_results['student_profiles'] = 0
    print(f"  ✓ student_profiles: {migration_results.get('student_profiles', 0)} inserted")

    # 10. Student Queries
    print("Migrating student_queries...")
    from app.models.student_query import StudentQuery as SQModel
    src_cur.execute("SELECT * FROM student_queries")
    sq_rows = src_cur.fetchall()
    if sq_rows:
        sq_cols = [d[0] for d in src_cur.description]
        sq_inserted = 0
        for row in sq_rows:
            data = dict(zip(sq_cols, row))
            existing = db.session.get(SQModel, data.get('id'))
            if existing:
                continue
            kwargs = {k: v for k, v in data.items() if hasattr(SQModel, k)}
            for dt_field in ['created_at', 'updated_at', 'resolved_at']:
                if dt_field in kwargs:
                    kwargs[dt_field] = parse_dt(kwargs[dt_field])
            try:
                obj = SQModel(**kwargs)
                db.session.add(obj)
                db.session.commit()
                sq_inserted += 1
            except Exception as e:
                db.session.rollback()
                print(f"    WARNING query id={data.get('id')}: {e}")
        migration_results['student_queries'] = sq_inserted
    else:
        migration_results['student_queries'] = 0
    print(f"  ✓ student_queries: {migration_results.get('student_queries', 0)} inserted")

    # 11. Student Login Activity
    print("Migrating student_login_activity...")
    from app.models.student_login_activity import StudentLoginActivity as SLAModel
    src_cur.execute("SELECT * FROM student_login_activity")
    sla_rows = src_cur.fetchall()
    if sla_rows:
        sla_cols = [d[0] for d in src_cur.description]
        sla_inserted = 0
        for row in sla_rows:
            data = dict(zip(sla_cols, row))
            existing = db.session.get(SLAModel, data.get('id'))
            if existing:
                continue
            kwargs = {k: v for k, v in data.items() if hasattr(SLAModel, k)}
            for dt_field in ['login_at', 'logout_at', 'last_activity_at', 'created_at']:
                if dt_field in kwargs:
                    kwargs[dt_field] = parse_dt(kwargs[dt_field])
            try:
                obj = SLAModel(**kwargs)
                db.session.add(obj)
                db.session.commit()
                sla_inserted += 1
            except Exception as e:
                db.session.rollback()
                print(f"    WARNING activity id={data.get('id')}: {e}")
        migration_results['student_login_activity'] = sla_inserted
    else:
        migration_results['student_login_activity'] = 0
    print(f"  ✓ student_login_activity: {migration_results.get('student_login_activity', 0)} inserted")

    # 12. Student Feedback
    print("Migrating student_feedback...")
    from app.models.student_feedback import StudentFeedback as SFModel
    src_cur.execute("SELECT * FROM student_feedback")
    sf_rows = src_cur.fetchall()
    if sf_rows:
        sf_cols = [d[0] for d in src_cur.description]
        sf_inserted = 0
        for row in sf_rows:
            data = dict(zip(sf_cols, row))
            existing = db.session.get(SFModel, data.get('id'))
            if existing:
                continue
            kwargs = {k: v for k, v in data.items() if hasattr(SFModel, k)}
            for dt_field in ['created_at', 'updated_at']:
                if dt_field in kwargs:
                    kwargs[dt_field] = parse_dt(kwargs[dt_field])
            try:
                obj = SFModel(**kwargs)
                db.session.add(obj)
                db.session.commit()
                sf_inserted += 1
            except Exception as e:
                db.session.rollback()
                print(f"    WARNING feedback id={data.get('id')}: {e}")
        migration_results['student_feedback'] = sf_inserted
    else:
        migration_results['student_feedback'] = 0
    print(f"  ✓ student_feedback: {migration_results.get('student_feedback', 0)} inserted")

    # --- Verification ---
    print(f"\n{'='*65}")
    print("  Verification: Source vs. Destination Row Counts")
    print(f"{'='*65}")

    all_passed = True
    for table, src_count in source_counts.items():
        # Query destination count
        try:
            result = db.session.execute(db.text(f'SELECT COUNT(*) FROM "{table}"'))
            dst_count = result.scalar()
        except Exception:
            dst_count = '?'

        status = '✓' if dst_count == src_count else '⚠'
        if dst_count != src_count:
            all_passed = False
        print(f"  {status} {table}: src={src_count}, dst={dst_count}")

    print(f"\n{'='*65}")
    if all_passed:
        print("  ✓ ALL COUNTS MATCH — Migration complete and verified!")
    else:
        print("  ⚠ Some counts differ. Check warnings above.")
        print("  Note: Rows already present in dst are counted; re-run is safe.")
    print(f"{'='*65}\n")

src_conn.close()
