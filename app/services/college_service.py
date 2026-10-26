from typing import Dict, Any, List, Optional
from sqlalchemy import or_, and_, func
from app import db
from app.models.college import College
from app.models.course import Course
from app.models.facility import Facility


class CollegeService:
    """Encapsulates all database operations, filters, search, and pagination for Colleges."""

    @staticmethod
    def get_college_by_id(college_id: int) -> Optional[College]:
        return db.session.get(College, college_id)

    @staticmethod
    def search_colleges(
        query: Optional[str] = None,
        course: Optional[str] = None,
        district: Optional[str] = None,
        city: Optional[str] = None,
        college_type: Optional[str] = None,
        autonomous: Optional[str] = None,
        data_status: Optional[str] = None,
        max_fee: Optional[float] = None,
        facilities: Optional[List[str]] = None,
        sort_by: str = 'name',
        page: int = 1,
        per_page: int = 9
    ) -> Dict[str, Any]:
        """
        Executes a filtered and paginated search across Tamil Nadu institutions.
        """
        # Base query joined with Course for course-level criteria
        stmt = db.session.query(College).distinct()

        # 1. Text Search across name, city, district, description, or code
        if query and query.strip():
            term = f"%{query.strip()}%"
            stmt = stmt.outerjoin(College.courses).filter(
                or_(
                    College.name.ilike(term),
                    College.city.ilike(term),
                    College.district.ilike(term),
                    College.code.ilike(term),
                    Course.course_name.ilike(term)
                )
            )

        # 2. Course Filter
        if course and course.strip() and course.lower() != 'all':
            stmt = stmt.join(College.courses).filter(
                Course.course_name.ilike(f"%{course.strip()}%")
            )

        # 3. Location Filters
        if district and district.strip() and district.lower() != 'all':
            from app.utils.district_normalizer import resolve_district_entity
            dist_obj = resolve_district_entity(district.strip())
            if dist_obj:
                stmt = stmt.filter(or_(College.district_id == dist_obj.id, College.district.ilike(dist_obj.name)))
            else:
                stmt = stmt.filter(College.district.ilike(district.strip()))

        if city and city.strip():
            stmt = stmt.filter(College.city.ilike(f"%{city.strip()}%"))

        # 4. College Type Filter (supports 8 institution types, legacy display names, and controlled vocabulary)
        if college_type and college_type.strip() and college_type.lower() != 'all':
            ctype = college_type.strip().lower()
            if ctype in ('autonomous', 'autonomous college'):
                stmt = stmt.filter(
                    or_(
                        College.autonomous_status == 'AUTONOMOUS',
                        College.college_type.ilike('%autonomous%'),
                        College.name.ilike('%autonomous%')
                    )
                )
            elif ctype in ('government', 'govt', 'government college'):
                stmt = stmt.filter(
                    or_(
                        College.primary_college_type == 'GOVERNMENT',
                        and_(College.college_type.ilike('%government%'), ~College.college_type.ilike('%aided%'))
                    )
                )
            elif ctype in ('government aided', 'government-aided', 'govt aided', 'aided'):
                stmt = stmt.filter(
                    or_(
                        College.primary_college_type == 'GOVERNMENT_AIDED',
                        College.college_type.ilike('%aided%')
                    )
                )
            elif ctype in ('self-financing', 'self financing', 'self_financing'):
                stmt = stmt.filter(
                    or_(
                        College.primary_college_type == 'SELF_FINANCING',
                        College.college_type.ilike('%self%')
                    )
                )
            elif ctype in ('private', 'private college'):
                stmt = stmt.filter(
                    or_(
                        College.primary_college_type == 'SELF_FINANCING',
                        College.college_type.ilike('%private%'),
                        College.college_type.ilike('%self%')
                    )
                )
            elif 'deemed' in ctype:
                stmt = stmt.filter(
                    or_(
                        College.college_type.ilike('%deemed%'),
                        College.name.ilike('%deemed%')
                    )
                )
            elif 'university' in ctype:
                stmt = stmt.filter(
                    or_(
                        College.college_type.ilike('%university%'),
                        College.name.ilike('%university%')
                    )
                )
            elif ctype == 'other':
                stmt = stmt.filter(
                    or_(
                        College.primary_college_type == 'OTHER',
                        College.college_type.ilike('%other%')
                    )
                )
            else:
                stmt = stmt.filter(
                    or_(
                        College.college_type.ilike(f"%{college_type.strip()}%"),
                        College.primary_college_type.ilike(f"%{college_type.strip()}%"),
                        func.replace(College.primary_college_type, '_', '-').ilike(f"%{college_type.strip()}%"),
                        func.replace(College.primary_college_type, '_', ' ').ilike(f"%{college_type.strip()}%")
                    )
                )

        # 4b. Autonomous Status Filter
        if autonomous and autonomous.strip() and autonomous.lower() != 'all':
            astat = autonomous.strip().upper()
            if astat in ('AUTONOMOUS', 'TRUE', 'YES'):
                stmt = stmt.filter(College.autonomous_status == 'AUTONOMOUS')
            elif astat in ('NON_AUTONOMOUS', 'NON-AUTONOMOUS', 'FALSE', 'NO'):
                stmt = stmt.filter(College.autonomous_status == 'NON_AUTONOMOUS')

        # 4c. Data Status Filter
        if data_status and data_status.strip() and data_status.lower() != 'all':
            stmt = stmt.filter(College.data_status.ilike(data_status.strip()))

        # 5. Maximum Annual Fee Filter
        if max_fee is not None and max_fee > 0:
            # If a specific course is chosen, filter that course's fee
            if course and course.strip() and course.lower() != 'all':
                stmt = stmt.filter(
                    Course.annual_fee.isnot(None),
                    Course.annual_fee <= max_fee
                )
            else:
                # Any course in the college meets budget
                stmt = stmt.join(College.courses).filter(
                    Course.annual_fee.isnot(None),
                    Course.annual_fee <= max_fee
                )

        # 6. Facility Filter (must have all selected facilities)
        if facilities and len(facilities) > 0:
            for fac in facilities:
                if fac and fac.strip():
                    fac_subquery = db.session.query(Facility.college_id).filter(
                        Facility.facility_name.ilike(fac.strip())
                    ).scalar_subquery()
                    stmt = stmt.filter(College.id.in_(fac_subquery))

        # 7. Sorting
        if sort_by == 'fee_asc':
            # Subquery min fee per college
            min_fee_sq = db.session.query(
                Course.college_id,
                func.min(Course.annual_fee).label('min_fee')
            ).group_by(Course.college_id).subquery()
            stmt = stmt.outerjoin(min_fee_sq, College.id == min_fee_sq.c.college_id).order_by(
                min_fee_sq.c.min_fee.asc().nullslast(),
                College.name.asc()
            )
        elif sort_by == 'fee_desc':
            max_fee_sq = db.session.query(
                Course.college_id,
                func.max(Course.annual_fee).label('max_fee')
            ).group_by(Course.college_id).subquery()
            stmt = stmt.outerjoin(max_fee_sq, College.id == max_fee_sq.c.college_id).order_by(
                max_fee_sq.c.max_fee.desc().nullslast(),
                College.name.asc()
            )
        elif sort_by == 'recent':
            stmt = stmt.order_by(College.last_updated.desc())
        else:
            # Default alphabetical
            stmt = stmt.order_by(College.name.asc())

        # 8. Pagination execution
        total = stmt.count()
        colleges = stmt.offset((page - 1) * per_page).limit(per_page).all()
        total_pages = max(1, (total + per_page - 1) // per_page)

        return {
            'colleges': [c.to_dict(include_details=True) for c in colleges],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'total_pages': total_pages,
                'has_prev': page > 1,
                'has_next': page < total_pages
            },
            'district_filtered': district.strip() if district and district.strip() and district.lower() != 'all' else None
        }

    @staticmethod
    def get_all_districts() -> List[str]:
        """Returns all 38 Tamil Nadu districts from the normalized District table."""
        from app.models.district import District
        districts = District.query.order_by(District.name.asc()).all()
        if districts:
            return [d.name for d in districts]
        rows = db.session.query(College.district).distinct().order_by(College.district.asc()).all()
        return [r[0] for r in rows if r[0]]

    @staticmethod
    def get_districts_detailed() -> List[dict]:
        """Returns all 38 districts with id, name, and current college count in database."""
        from app.models.district import District
        districts = District.query.order_by(District.name.asc()).all()
        return [d.to_dict(include_counts=True) for d in districts]

    @staticmethod
    def get_all_courses() -> List[str]:
        rows = db.session.query(Course.course_name).distinct().order_by(Course.course_name.asc()).all()
        return [r[0] for r in rows if r[0]]

    @staticmethod
    def get_all_college_types() -> List[str]:
        return [
            'Government',
            'Government Aided',
            'Autonomous',
            'Self-Financing',
            'Private',
            'Deemed University',
            'University Department',
            'Other'
        ]

    @staticmethod
    def get_all_facilities() -> List[str]:
        rows = db.session.query(Facility.facility_name).distinct().order_by(Facility.facility_name.asc()).all()
        return [r[0] for r in rows if r[0]]
