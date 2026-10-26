from typing import List, Dict, Any, Tuple
import numpy as np
import pandas as pd
from sklearn.preprocessing import OneHotEncoder
from app.models.college import College


class CollegeFeatureExtractor:
    """
    Transforms relational College, Course, and Facility models into structured
    numerical and categorical matrices for content-based recommendation.
    """

    @staticmethod
    def extract_dataset(colleges: List[College]) -> pd.DataFrame:
        """Constructs a clean pandas DataFrame from SQLAlchemy College models."""
        rows = []
        for c in colleges:
            courses = [crs.course_name for crs in c.courses]
            fees = [crs.annual_fee for crs in c.courses if crs.annual_fee is not None]
            min_fee = min(fees) if fees else None
            avg_fee = sum(fees) / len(fees) if fees else None
            facilities = [f.facility_name for f in c.facilities]

            rows.append({
                'college_id': c.id,
                'name': c.name,
                'state': c.state,
                'district': c.district,
                'city': c.city,
                'college_type': c.college_type,
                'primary_college_type': getattr(c, 'primary_college_type', 'UNKNOWN'),
                'autonomous_status': getattr(c, 'autonomous_status', 'UNKNOWN'),
                'is_autonomous': getattr(c, 'is_autonomous', False),
                'courses': courses,
                'facilities': facilities,
                'min_fee': min_fee,
                'avg_fee': avg_fee,
                'data_status': c.data_status,
                'official_website': c.official_website or c.official_website_url,
                'official_website_url': c.official_website_url or c.official_website,
                'latitude': c.latitude,
                'longitude': c.longitude,
                'has_coordinates': c.has_valid_coordinates
            })
        return pd.DataFrame(rows)

    @staticmethod
    def build_preference_vector(user_pref: Dict[str, Any], all_districts: List[str], all_types: List[str]) -> Dict[str, Any]:
        """Normalizes user preferences into structured query attributes."""
        return {
            'target_course': user_pref.get('course', '').strip(),
            'target_district': user_pref.get('district', '').strip(),
            'target_city': user_pref.get('city', '').strip(),
            'target_type': user_pref.get('college_type', '').strip(),
            'target_autonomous': user_pref.get('autonomous', '').strip(),
            'max_budget': float(user_pref['budget']) if user_pref.get('budget') not in (None, '') else None,
            'desired_facilities': [f.strip() for f in user_pref.get('facilities', []) if f and f.strip()]
        }
