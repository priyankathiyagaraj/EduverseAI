from typing import Dict, Any, Tuple, List, Optional
from flask import session
from app import db
from app.models.college import College
from app.models.preference import StudentPreference
from app.recommender.recommender import ContentBasedRecommender


class RecommendationService:
    DISCLAIMER = "Recommendations are informational and depend on the quality and freshness of available data. Verify admission requirements and fees with official sources."

    @staticmethod
    def validate_preference_payload(data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        budget = data.get('budget')
        if budget is not None and budget != '':
            try:
                b_val = float(budget)
                if b_val < 0:
                    return False, "Budget must be a non-negative number."
            except ValueError:
                return False, "Budget must be a valid numerical value."

        facilities = data.get('facilities')
        if facilities is not None and not isinstance(facilities, list):
            return False, "Facilities must be provided as a list of strings."

        return True, None

    @staticmethod
    def get_recommendations(pref_data: Dict[str, Any], top_k: int = 10) -> Dict[str, Any]:
        """
        Executes the content-based recommendation workflow.
        """
        valid, err = RecommendationService.validate_preference_payload(pref_data)
        if not valid:
            raise ValueError(err)

        # If specific district requested, verify if college records exist for it
        target_district = pref_data.get('district')
        if target_district and target_district.strip() and target_district.lower() not in ('all', 'any'):
            from sqlalchemy import or_
            from app.utils.district_normalizer import resolve_district_entity
            dist_obj = resolve_district_entity(target_district.strip())
            if dist_obj:
                colleges_in_district = College.query.filter(
                    or_(College.district_id == dist_obj.id, College.district.ilike(dist_obj.name))
                ).count()
                resolved_district_name = dist_obj.name
            else:
                colleges_in_district = College.query.filter(College.district.ilike(target_district.strip())).count()
                resolved_district_name = target_district.strip()

            if colleges_in_district == 0:
                return {
                    'recommendations': [],
                    'count': 0,
                    'message': "No college information is currently available for the selected district.",
                    'disclaimer': RecommendationService.DISCLAIMER,
                    'preferences_applied': {
                        'course': pref_data.get('course') or 'Any',
                        'district': resolved_district_name,
                        'city': pref_data.get('city') or 'Any',
                        'budget': pref_data.get('budget'),
                        'college_type': pref_data.get('college_type') or 'Any',
                        'autonomous': pref_data.get('autonomous') or 'Any',
                        'facilities': pref_data.get('facilities', [])
                    }
                }

        # Fetch all candidate colleges
        colleges = College.query.all()
        recommender = ContentBasedRecommender()
        ranked = recommender.recommend(colleges, pref_data, top_k=top_k)

        # If user logged in, persist their search preferences
        from flask import has_request_context
        if has_request_context():
            user = session.get('user')
            if user and 'id' in user:
                try:
                    pref = StudentPreference(
                        user_id=user['id'],
                        course_name=pref_data.get('course'),
                        district=pref_data.get('district'),
                        city=pref_data.get('city'),
                        budget=float(pref_data['budget']) if pref_data.get('budget') else None,
                        college_type=pref_data.get('college_type')
                    )
                    if pref_data.get('facilities'):
                        pref.set_facilities_list(pref_data['facilities'])
                    db.session.add(pref)
                    db.session.commit()
                except Exception:
                    db.session.rollback()

        return {
            'recommendations': ranked,
            'count': len(ranked),
            'disclaimer': RecommendationService.DISCLAIMER,
            'preferences_applied': {
                'course': pref_data.get('course') or 'Any',
                'district': pref_data.get('district') or 'Any',
                'city': pref_data.get('city') or 'Any',
                'budget': pref_data.get('budget'),
                'college_type': pref_data.get('college_type') or 'Any',
                'autonomous': pref_data.get('autonomous') or 'Any',
                'facilities': pref_data.get('facilities', [])
            }
        }
