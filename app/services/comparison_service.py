from typing import List, Dict, Any, Tuple, Optional
from flask import session
from app import db
from app.models.college import College
from app.models.comparison import ComparisonItem


class ComparisonService:
    MAX_COLLEGES = 4
    MIN_COLLEGES = 2

    @staticmethod
    def get_comparison_ids() -> List[int]:
        """Returns list of college IDs currently in comparison (from session or database)."""
        compare_list = session.get('compare_list', [])
        # Ensure unique integers
        return [int(cid) for cid in compare_list if str(cid).isdigit()]

    @staticmethod
    def add_college(college_id: int) -> Tuple[bool, str, int]:
        """
        Adds a college to the comparison list.
        Enforces maximum of 4 colleges and duplicate prevention.
        Returns (success, message, current_count).
        """
        college = db.session.get(College, college_id)
        if not college:
            return False, "College does not exist.", len(ComparisonService.get_comparison_ids())

        compare_list = ComparisonService.get_comparison_ids()

        if college_id in compare_list:
            return False, f"'{college.name}' is already in your comparison matrix.", len(compare_list)

        if len(compare_list) >= ComparisonService.MAX_COLLEGES:
            return False, f"You can compare at most {ComparisonService.MAX_COLLEGES} institutions simultaneously. Remove one to add another.", len(compare_list)

        compare_list.append(college_id)
        session['compare_list'] = compare_list
        session.modified = True

        # If user is logged in, optionally persist to database
        user = session.get('user')
        if user and 'id' in user:
            try:
                existing = ComparisonItem.query.filter_by(user_id=user['id'], college_id=college_id).first()
                if not existing:
                    item = ComparisonItem(user_id=user['id'], college_id=college_id)
                    db.session.add(item)
                    db.session.commit()
            except Exception:
                db.session.rollback()

        return True, f"Added '{college.name}' to comparison.", len(compare_list)

    @staticmethod
    def remove_college(college_id: int) -> Tuple[bool, str, int]:
        """Removes a college from comparison list."""
        compare_list = ComparisonService.get_comparison_ids()

        if college_id in compare_list:
            compare_list.remove(college_id)
            session['compare_list'] = compare_list
            session.modified = True

            # If user is logged in, remove from database
            user = session.get('user')
            if user and 'id' in user:
                try:
                    ComparisonItem.query.filter_by(user_id=user['id'], college_id=college_id).delete()
                    db.session.commit()
                except Exception:
                    db.session.rollback()

            return True, "Removed college from comparison.", len(compare_list)

        return False, "College was not found in comparison list.", len(compare_list)

    @staticmethod
    def clear_all() -> Tuple[bool, str]:
        """Clears all colleges from comparison."""
        session['compare_list'] = []
        session.modified = True

        user = session.get('user')
        if user and 'id' in user:
            try:
                ComparisonItem.query.filter_by(user_id=user['id']).delete()
                db.session.commit()
            except Exception:
                db.session.rollback()

        return True, "Cleared all comparison items."

    @staticmethod
    def get_comparison_data() -> Dict[str, Any]:
        """
        Retrieves detailed comparison data for selected colleges,
        formatting factual matrices side by side.
        """
        college_ids = ComparisonService.get_comparison_ids()
        colleges = College.query.filter(College.id.in_(college_ids)).all() if college_ids else []

        # Maintain insertion order
        colleges_dict = {c.id: c for c in colleges}
        ordered_colleges = [colleges_dict[cid] for cid in college_ids if cid in colleges_dict]

        formatted_list = [c.to_dict(include_details=True) for c in ordered_colleges]

        # Gather union of all facilities across these colleges to compare presence/absence
        all_facilities = sorted(list(set(
            fac for c in formatted_list for fac in c.get('facilities', [])
        )))

        # Gather union of all courses across these colleges
        all_courses = sorted(list(set(
            crs['course_name'] for c in formatted_list for crs in c.get('courses', [])
        )))

        return {
            'colleges': formatted_list,
            'count': len(formatted_list),
            'min_required': ComparisonService.MIN_COLLEGES,
            'max_allowed': ComparisonService.MAX_COLLEGES,
            'is_ready': len(formatted_list) >= ComparisonService.MIN_COLLEGES,
            'all_facilities': all_facilities,
            'all_courses': all_courses
        }
