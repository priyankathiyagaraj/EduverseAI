from typing import Dict, Any, List
from sqlalchemy import func, or_
from app import db
from app.models.college import College
from app.models.course import Course
from app.models.facility import Facility


class AnalyticsService:
    """Computes real-time analytical metrics and distributions derived strictly from live database records."""

    @staticmethod
    def get_analytics_metrics() -> Dict[str, Any]:
        from app.models.district import District

        # 1. Total counts
        total_colleges = db.session.query(func.count(College.id)).scalar() or 0
        total_courses = db.session.query(func.count(Course.id)).scalar() or 0
        all_districts = District.query.order_by(District.name.asc()).all()
        total_districts_supported = len(all_districts) if all_districts else 38
        total_facilities = db.session.query(func.count(Facility.id)).scalar() or 0

        # Latest update timestamp
        latest_update = db.session.query(func.max(College.last_updated)).scalar()
        latest_update_str = latest_update.strftime('%Y-%m-%d %H:%M UTC') if latest_update else 'N/A'

        # 2. Colleges by District (All 38 Tamil Nadu districts dynamically calculated)
        district_counts_by_id = {
            row[0]: row[1]
            for row in db.session.query(
                College.district_id,
                func.count(College.id)
            ).filter(College.district_id.isnot(None)).group_by(College.district_id).all()
        }
        district_counts_by_name = {
            row[0]: row[1]
            for row in db.session.query(
                College.district,
                func.count(College.id)
            ).group_by(College.district).all()
        }

        district_labels = []
        district_data = []
        district_status_notes = []

        if all_districts:
            for d in all_districts:
                c = district_counts_by_id.get(d.id, district_counts_by_name.get(d.name, 0))
                district_labels.append(d.name)
                district_data.append(c)
                if c == 0:
                    district_status_notes.append("0 colleges currently available in EduVerse database")
                else:
                    district_status_notes.append(f"{c} college{'s' if c != 1 else ''} cataloged")
        else:
            # Fallback if districts not yet seeded
            for name, count in sorted(district_counts_by_name.items()):
                district_labels.append(name)
                district_data.append(count)
                district_status_notes.append(f"{count} college{'s' if count != 1 else ''} cataloged")

        populated_count = len([c for c in district_data if c > 0])

        colleges_by_district = {
            'labels': district_labels,
            'counts': district_data,
            'status_notes': district_status_notes,
            'total_districts_supported': total_districts_supported,
            'districts_with_colleges': populated_count,
            'districts_without_colleges': total_districts_supported - populated_count
        }

        # 3. College Distribution by Type
        type_rows = db.session.query(
            College.college_type,
            func.count(College.id).label('count')
        ).group_by(College.college_type).order_by(func.count(College.id).desc()).all()

        colleges_by_type = {
            'labels': [r[0] for r in type_rows],
            'counts': [r[1] for r in type_rows]
        }

        # 4. Course Availability (Top programs offered)
        course_rows = db.session.query(
            Course.course_name,
            func.count(Course.id).label('count')
        ).group_by(Course.course_name).order_by(func.count(Course.id).desc()).limit(8).all()

        courses_availability = {
            'labels': [r[0] for r in course_rows],
            'counts': [r[1] for r in course_rows]
        }

        # 5. Annual Fee Distribution
        all_fees = db.session.query(Course.annual_fee).all()
        fee_brackets = {
            'Under ₹25,000': 0,
            '₹25,000 - ₹50,000': 0,
            '₹50,000 - ₹1,00,000': 0,
            '₹1,00,000 - ₹1,50,000': 0,
            'Above ₹1,50,000': 0,
            'Fee Not Published': 0
        }

        for (fee,) in all_fees:
            if fee is None:
                fee_brackets['Fee Not Published'] += 1
            elif fee < 25000:
                fee_brackets['Under ₹25,000'] += 1
            elif fee <= 50000:
                fee_brackets['₹25,000 - ₹50,000'] += 1
            elif fee <= 100000:
                fee_brackets['₹50,000 - ₹1,00,000'] += 1
            elif fee <= 150000:
                fee_brackets['₹1,00,000 - ₹1,50,000'] += 1
            else:
                fee_brackets['Above ₹1,50,000'] += 1

        fee_distribution = {
            'labels': list(fee_brackets.keys()),
            'counts': list(fee_brackets.values())
        }

        # 6. Data Status Transparency Split
        status_rows = db.session.query(
            College.data_status,
            func.count(College.id).label('count')
        ).group_by(College.data_status).all()

        data_status_breakdown = {
            'labels': [r[0] for r in status_rows],
            'counts': [r[1] for r in status_rows]
        }

        # 7. Autonomous vs Non-Autonomous Distribution
        auto_count = db.session.query(func.count(College.id)).filter(
            or_(College.autonomous_status == 'AUTONOMOUS', College.name.ilike('%(autonomous)%'))
        ).scalar() or 0
        non_auto_count = total_colleges - auto_count

        autonomous_distribution = {
            'labels': ['Autonomous', 'Non-Autonomous'],
            'counts': [auto_count, non_auto_count]
        }

        # 8. Ownership Distribution (Controlled Vocabulary)
        gov_count = db.session.query(func.count(College.id)).filter(
            or_(College.primary_college_type == 'GOVERNMENT', College.college_type == 'Government')
        ).scalar() or 0
        aided_count = db.session.query(func.count(College.id)).filter(
            or_(College.primary_college_type == 'GOVERNMENT_AIDED', College.college_type == 'Government-Aided')
        ).scalar() or 0
        sf_count = db.session.query(func.count(College.id)).filter(
            or_(College.primary_college_type == 'SELF_FINANCING', College.college_type == 'Self-Financing')
        ).scalar() or 0
        other_ownership_count = total_colleges - (gov_count + aided_count + sf_count)

        ownership_distribution = {
            'labels': ['Government', 'Government-Aided', 'Self-Financing', 'Other / Central / Deemed'],
            'counts': [gov_count, aided_count, sf_count, max(0, other_ownership_count)]
        }

        # 9. Top Cities
        city_rows = db.session.query(
            College.city,
            func.count(College.id).label('count')
        ).group_by(College.city).order_by(func.count(College.id).desc()).limit(10).all()

        colleges_by_city = {
            'labels': [r[0] for r in city_rows if r[0]],
            'counts': [r[1] for r in city_rows if r[0]]
        }

        return {
            'summary': {
                'total_colleges': total_colleges,
                'total_courses': total_courses,
                'total_districts': total_districts_supported,
                'total_districts_supported': total_districts_supported,
                'districts_with_colleges': populated_count,
                'districts_without_colleges': total_districts_supported - populated_count,
                'total_facilities': total_facilities,
                'government_count': gov_count,
                'aided_count': aided_count,
                'self_financing_count': sf_count,
                'autonomous_count': auto_count,
                'last_updated': latest_update_str
            },
            'colleges_by_district': colleges_by_district,
            'colleges_by_type': colleges_by_type,
            'ownership_distribution': ownership_distribution,
            'autonomous_distribution': autonomous_distribution,
            'colleges_by_city': colleges_by_city,
            'courses_availability': courses_availability,
            'fee_distribution': fee_distribution,
            'data_status_breakdown': data_status_breakdown
        }
