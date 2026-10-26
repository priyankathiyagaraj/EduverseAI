from typing import Dict, Any, List, Tuple


class RecommendationScorer:
    """
    Transparent, configurable multi-criteria scoring model with explainable factor generation.
    Weights sum to 1.0 (100%).
    """

    # Configurable weights
    DEFAULT_WEIGHTS = {
        'course': 0.35,
        'location': 0.25,
        'budget': 0.20,
        'college_type': 0.10,
        'facilities': 0.10
    }

    def __init__(self, weights: Dict[str, float] = None):
        self.weights = weights or self.DEFAULT_WEIGHTS
        # Ensure normalization
        total_w = sum(self.weights.values())
        if abs(total_w - 1.0) > 1e-4:
            self.weights = {k: v / total_w for k, v in self.weights.items()}

    def calculate_score_and_factors(self, college: Dict[str, Any], pref: Dict[str, Any]) -> Tuple[float, List[str], Dict[str, float]]:
        """
        Calculates normalized score (0.0 to 100.0) and generates human-readable explainable match factors.
        """
        factors: List[str] = []
        sub_scores: Dict[str, float] = {}

        # 1. Course Match (Weight: 0.35)
        target_course = pref.get('target_course', '').lower()
        college_courses = [c.lower() for c in college.get('courses', [])]

        if not target_course:
            s_course = 1.0  # User didn't specify course; neutral full score
        else:
            exact_match = any(target_course == c for c in college_courses)
            partial_match = any(target_course in c or c in target_course for c in college_courses)
            if exact_match:
                s_course = 1.0
                factors.append(f"✓ {pref.get('target_course')} program is offered at this institution.")
            elif partial_match:
                s_course = 0.7
                factors.append(f"✓ Related computer/technology specialization offered.")
            else:
                s_course = 0.0
        sub_scores['course'] = s_course

        # 2. Location Affinity (Weight: 0.25)
        target_district = pref.get('target_district', '').lower()
        target_city = pref.get('target_city', '').lower()
        college_district = college.get('district', '').lower()
        college_city = college.get('city', '').lower()

        if not target_district and not target_city:
            s_loc = 1.0
        else:
            city_match = bool(target_city and target_city in college_city)
            dist_match = bool(target_district and target_district in college_district)

            if city_match:
                s_loc = 1.0
                factors.append(f"✓ Located directly in your preferred city of {college.get('city')}.")
            elif dist_match:
                s_loc = 0.85
                factors.append(f"✓ Located in your preferred district of {college.get('district')}.")
            else:
                # Same state (Tamil Nadu), different district
                s_loc = 0.25
        sub_scores['location'] = s_loc

        # 3. Budget Compatibility (Weight: 0.20)
        budget = pref.get('max_budget')
        min_fee = college.get('min_fee')

        if budget is None or budget <= 0:
            s_budget = 1.0
        elif min_fee is None:
            # Missing fee data: neutral confidence penalty, explicit notice
            s_budget = 0.5
            factors.append("ℹ Tuition fee schedule not published; verify with admission office.")
        elif min_fee <= budget:
            # Under budget: score 0.8 to 1.0 depending on how comfortably it fits
            ratio = min_fee / budget
            s_budget = 1.0 - (0.15 * ratio)
            factors.append(f"✓ Within your specified annual budget ceiling of ₹{budget:,.0f} (starting at ₹{min_fee:,.0f}).")
        else:
            # Exceeds budget: decay smoothly
            over_ratio = (min_fee - budget) / budget
            s_budget = max(0.0, 1.0 - over_ratio)
            if s_budget > 0.4:
                factors.append(f"△ Annual tuition (₹{min_fee:,.0f}) slightly exceeds your preferred budget limit.")
        sub_scores['budget'] = s_budget

        # 4. College Type & Autonomy Match (Weight: 0.10)
        target_type = pref.get('target_type', '')
        college_type = college.get('college_type', '')
        primary_type = college.get('primary_college_type', '')
        autonomous_status = college.get('autonomous_status', '')
        is_autonomous = college.get('is_autonomous', False) or autonomous_status == 'AUTONOMOUS'

        if not target_type or target_type.lower() in ('all', ''):
            s_type = 1.0
        else:
            tt_lower = target_type.lower()
            ct_lower = college_type.lower()
            pt_lower = primary_type.lower().replace('_', '-')

            # Check for direct match or ownership match or autonomy match
            if tt_lower == 'autonomous':
                if is_autonomous or 'autonomous' in ct_lower:
                    s_type = 1.0
                    factors.append(f"✓ Matches your preference for an Autonomous institution.")
                else:
                    s_type = 0.3
            elif tt_lower in (ct_lower, pt_lower) or (tt_lower in ('government', 'govt') and ('government' in ct_lower or 'government' in pt_lower)) or (tt_lower in ('aided', 'government-aided', 'govt-aided') and ('aided' in ct_lower or 'aided' in pt_lower)) or (tt_lower in ('self-financing', 'private') and ('self' in ct_lower or 'self' in pt_lower)):
                s_type = 1.0
                factors.append(f"✓ Matches your preferred institution type ({college_type}).")
            else:
                s_type = 0.3

        # Autonomy preference check if explicitly specified
        target_auto = pref.get('target_autonomous', '').upper()
        if target_auto in ('AUTONOMOUS', 'TRUE', 'YES'):
            if is_autonomous:
                factors.append("✓ Autonomous curriculum status verified.")
            else:
                s_type *= 0.5
        elif target_auto in ('NON_AUTONOMOUS', 'NON-AUTONOMOUS', 'FALSE', 'NO'):
            if is_autonomous:
                s_type *= 0.5

        sub_scores['type'] = round(s_type, 2)

        # 5. Facility Coverage (Weight: 0.10)
        desired_facs = [f.lower() for f in pref.get('desired_facilities', [])]
        college_facs = [f.lower() for f in college.get('facilities', [])]

        if not desired_facs:
            s_fac = 1.0
        else:
            matched_facs = [f for f in desired_facs if any(f in cf or cf in f for cf in college_facs)]
            s_fac = len(matched_facs) / len(desired_facs)
            if matched_facs:
                readable = ", ".join([f.title() for f in matched_facs[:3]])
                factors.append(f"✓ Provides requested facilities: {readable}.")
            if s_fac < 1.0 and len(matched_facs) > 0:
                missing_count = len(desired_facs) - len(matched_facs)
                factors.append(f"ℹ {missing_count} requested campus amenities not recorded.")
        sub_scores['facilities'] = s_fac

        # Final Weighted Score Calculation
        weighted_sum = (
            self.weights['course'] * s_course +
            self.weights['location'] * s_loc +
            self.weights['budget'] * s_budget +
            self.weights['college_type'] * s_type +
            self.weights['facilities'] * s_fac
        )

        final_percentage = round(weighted_sum * 100.0, 1)

        # Transparency disclaimer tag
        if college.get('data_status') == 'SAMPLE':
            factors.append("⚠️ Sample test record used for academic development.")

        return final_percentage, factors, sub_scores
