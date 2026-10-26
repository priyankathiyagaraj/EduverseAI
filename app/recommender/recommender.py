from typing import List, Dict, Any
import numpy as np
from app.models.college import College
from app.recommender.feature_engineering import CollegeFeatureExtractor
from app.recommender.scoring import RecommendationScorer


class ContentBasedRecommender:
    """
    Intelligent Recommendation Engine combining multi-criteria preference scoring
    with scikit-learn feature encoding and explainable match diagnostics.
    """

    def __init__(self, scorer: RecommendationScorer = None):
        self.scorer = scorer or RecommendationScorer()

    def recommend(self, colleges: List[College], user_pref: Dict[str, Any], top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Generates ranked college recommendations based on user preference vector.
        Does NOT merely filter; evaluates multi-attribute similarity and produces explainable scores.
        """
        if not colleges:
            return []

        # 1. Feature extraction
        df = CollegeFeatureExtractor.extract_dataset(colleges)
        pref_vec = CollegeFeatureExtractor.build_preference_vector(user_pref, [], [])

        results = []
        for _, row in df.iterrows():
            college_dict = row.to_dict()
            score, factors, sub_scores = self.scorer.calculate_score_and_factors(college_dict, pref_vec)

            # Minimum score threshold to filter out completely irrelevant colleges (e.g. course didn't match and other fields 0)
            # If user specified a course, prioritize institutions with that course or positive course score
            if pref_vec.get('target_course') and sub_scores.get('course', 0) == 0:
                # Do not recommend colleges that completely lack the desired course
                continue

            results.append({
                'college_id': college_dict['college_id'],
                'college_name': college_dict['name'],
                'score': score,
                'matching_factors': factors,
                'sub_scores': sub_scores,
                'location': f"{college_dict['city']}, {college_dict['district']}",
                'district': college_dict['district'],
                'city': college_dict['city'],
                'college_type': college_dict['college_type'],
                'primary_college_type': college_dict.get('primary_college_type', 'UNKNOWN'),
                'autonomous_status': college_dict.get('autonomous_status', 'UNKNOWN'),
                'is_autonomous': college_dict.get('is_autonomous', False),
                'fee': college_dict['min_fee'],
                'data_status': college_dict['data_status'],
                'official_website': college_dict.get('official_website') or college_dict.get('official_website_url'),
                'official_website_url': college_dict.get('official_website_url') or college_dict.get('official_website'),
                'courses': college_dict['courses'],
                'facilities': college_dict['facilities'],
                'has_coordinates': college_dict['has_coordinates'],
                'latitude': college_dict['latitude'],
                'longitude': college_dict['longitude']
            })

        # Rank descending by score
        results.sort(key=lambda x: x['score'], reverse=True)

        return results[:top_k]
