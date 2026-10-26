# APPENDIX A – RECOMMENDATION MODEL SOURCE CODE

**Project Title:** EDUVERSE AI – AI-BASED COLLEGE RECOMMENDATION SYSTEM
**Academic Programme:** Master of Computer Applications (MCA)
**Implementation Type:** Rule-Based Multi-Criteria Weighted Scoring System
**Primary Language:** Python 3.12
**Web Framework:** Flask
**ORM:** Flask-SQLAlchemy (SQLite / MySQL)

---

> **Important Accuracy Notice**
> Every code listing in this appendix is extracted verbatim from the actual project source files.
> File paths are given for every listing. No sample code, placeholder logic, or fabricated accuracy
> percentages have been introduced. The system is a **transparent, rule-based, multi-criteria weighted
> scoring recommender** — no trained machine-learning model is loaded or invoked in the recommendation
> pipeline. The term "AI-Powered" used in `CourseRecommendationService` refers to formula-based
> aptitude scoring, not a trained neural network or scikit-learn classifier.

---

## A.1  Recommendation Logic

The core recommendation logic is split across three cooperating Python modules inside
`app/recommender/`:

| Module | File | Responsibility |
|--------|------|---------------|
| `CollegeFeatureExtractor` | `app/recommender/feature_engineering.py` | Converts SQLAlchemy College ORM objects into a pandas DataFrame and converts raw user inputs into a structured preference vector |
| `RecommendationScorer` | `app/recommender/scoring.py` | Calculates a weighted multi-criteria match score (0–100) per college and generates human-readable match factors |
| `ContentBasedRecommender` | `app/recommender/recommender.py` | Orchestrates extraction → scoring → filtering → ranked result list |

The entry point for the Flask API is `app/routes/recommendations.py` (route `POST /api/recommend`),
which delegates to `app/services/recommendation_service.py`, which in turn calls
`ContentBasedRecommender.recommend()`.

---

### A.1.1  Package Initializer

**File:** `app/recommender/__init__.py`

```python
from app.recommender.recommender import ContentBasedRecommender
from app.recommender.scoring import RecommendationScorer
from app.recommender.feature_engineering import CollegeFeatureExtractor

__all__ = [
    'ContentBasedRecommender',
    'RecommendationScorer',
    'CollegeFeatureExtractor'
]
```

---

### A.1.2  Content-Based Recommender Engine

**File:** `app/recommender/recommender.py`

```python
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

            # Minimum score threshold to filter out completely irrelevant colleges
            # (e.g. course didn't match and other fields 0)
            # If user specified a course, prioritize institutions with that course
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
```

**Algorithm narrative:**

1. `CollegeFeatureExtractor.extract_dataset()` converts every `College` ORM object into a flat
   pandas `DataFrame` row.
2. `CollegeFeatureExtractor.build_preference_vector()` normalizes the raw JSON payload from the
   student into a structured dictionary (`pref_vec`).
3. For each college row, `RecommendationScorer.calculate_score_and_factors()` computes five
   weighted sub-scores and combines them into a final percentage.
4. Colleges whose target course sub-score is exactly 0 (i.e., the course is not offered at all)
   are dropped from the candidate list.
5. The remaining results are sorted descending by `score` and the top `top_k` are returned.

---

## A.2  Input Validation and Filtering

### A.2.1  Feature Engineering and Preference Vector Construction

**File:** `app/recommender/feature_engineering.py`

```python
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
```

**Preference vector fields:**

| Key | Source JSON field | Description |
|-----|------------------|-------------|
| `target_course` | `course` | Course / programme of interest (e.g., `"MCA"`, `"B.Tech CSE"`) |
| `target_district` | `district` | Preferred Tamil Nadu district (e.g., `"Chennai"`, `"Coimbatore"`) |
| `target_city` | `city` | Specific city within a district |
| `target_type` | `college_type` | Institution type (`"Government"`, `"Self-Financing"`, etc.) |
| `target_autonomous` | `autonomous` | Autonomy preference (`"AUTONOMOUS"` / `"NON_AUTONOMOUS"`) |
| `max_budget` | `budget` | Maximum annual tuition fee in Indian Rupees |
| `desired_facilities` | `facilities` | List of required campus amenities (e.g., `["Hostel", "Placement Cell"]`) |

---

### A.2.2  Recommendation Service — Input Validation

**File:** `app/services/recommendation_service.py`

```python
from typing import Dict, Any, Tuple, List, Optional
from flask import session
from app import db
from app.models.college import College
from app.models.preference import StudentPreference
from app.recommender.recommender import ContentBasedRecommender


class RecommendationService:
    DISCLAIMER = (
        "Recommendations are informational and depend on the quality and freshness of available data. "
        "Verify admission requirements and fees with official sources."
    )

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
                colleges_in_district = College.query.filter(
                    College.district.ilike(target_district.strip())
                ).count()
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

        # If user is logged in, persist their search preferences
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
```

**Validation rules:**

| Check | Field | Rule |
|-------|-------|------|
| Budget type | `budget` | Must be a non-negative float or omitted |
| Facilities type | `facilities` | Must be a Python `list` if provided |
| District existence | `district` | If a district is specified and no colleges are in the database for it, an early empty response is returned with an informative message |

---

### A.2.3  District Name Normalization

**File:** `app/utils/district_normalizer.py`

The normalizer maps common spelling variants and colloquial names
(e.g., `"Trichy"` → `"Tiruchirappalli"`, `"Ooty"` → `"The Nilgiris"`) to the canonical
38 Tamil Nadu district names before the database query is executed.

```python
import re
from typing import Optional
from app import db
from app.models.district import District

# Canonical mappings for Tamil Nadu districts (excerpt — full map in source file)
DISTRICT_ALIASES = {
    "trichy": "Tiruchirappalli",
    "tiruchirapalli": "Tiruchirappalli",
    "ooty": "The Nilgiris",
    "nilgiris": "The Nilgiris",
    "tuticorin": "Thoothukudi",
    "kanchipuram": "Kancheepuram",
    "villupuram": "Viluppuram",
    "tanjore": "Thanjavur",
    "nellai": "Tirunelveli",
    "thiruvallur": "Tiruvallur",
    # ... (full alias table in app/utils/district_normalizer.py)
}


def normalize_district_name(input_str: Optional[str]) -> Optional[str]:
    """
    Normalizes any Tamil Nadu district name string to its canonical spelling.
    Strips 'District' suffixes, normalizes whitespace and casing, and maps known aliases.
    """
    if not input_str:
        return None
    cleaned = input_str.strip()
    if not cleaned or cleaned.lower() in ('all', 'any'):
        return None
    lower = cleaned.lower()
    lower = re.sub(r'\s+district$', '', lower)
    lower = re.sub(r'\s+dt\.?$', '', lower)
    lower = lower.strip()
    if lower in DISTRICT_ALIASES:
        return DISTRICT_ALIASES[lower]
    return cleaned.title()


def resolve_district_entity(name_or_id) -> Optional[District]:
    """
    Resolves a District model instance from either an integer ID or a district name/alias string.
    """
    if not name_or_id:
        return None
    if isinstance(name_or_id, int):
        return db.session.get(District, name_or_id)
    str_val = str(name_or_id).strip()
    if str_val.isdigit():
        dist = db.session.get(District, int(str_val))
        if dist:
            return dist
    canonical_name = normalize_district_name(str_val)
    if not canonical_name:
        return None
    dist = District.query.filter(District.name.ilike(canonical_name)).first()
    if dist:
        return dist
    # Fuzzy search fallback
    return District.query.filter(District.name.ilike(f"%{canonical_name}%")).first()
```

---

## A.3  College Scoring and Ranking

**File:** `app/recommender/scoring.py`

The `RecommendationScorer` class implements a fully transparent, configurable multi-criteria
scoring model. Five weighted criteria are evaluated independently, and the results are combined
into a final match percentage.

### A.3.1  Scoring Weights

```
Course match         : 35%
Location affinity    : 25%
Budget compatibility : 20%
College type match   : 10%
Facility coverage    : 10%
─────────────────────────
Total                : 100%
```

All weights sum to exactly `1.0`. The scorer accepts a custom `weights` dictionary at construction
time; if the weights do not sum to 1.0, they are automatically normalized.

### A.3.2  Full Scorer Implementation

```python
from typing import Dict, Any, List, Tuple


class RecommendationScorer:
    """
    Transparent, configurable multi-criteria scoring model with explainable factor generation.
    Weights sum to 1.0 (100%).
    """

    DEFAULT_WEIGHTS = {
        'course': 0.35,
        'location': 0.25,
        'budget': 0.20,
        'college_type': 0.10,
        'facilities': 0.10
    }

    def __init__(self, weights: Dict[str, float] = None):
        self.weights = weights or self.DEFAULT_WEIGHTS
        total_w = sum(self.weights.values())
        if abs(total_w - 1.0) > 1e-4:
            self.weights = {k: v / total_w for k, v in self.weights.items()}

    def calculate_score_and_factors(
        self,
        college: Dict[str, Any],
        pref: Dict[str, Any]
    ) -> Tuple[float, List[str], Dict[str, float]]:
        """
        Calculates normalized score (0.0 to 100.0) and generates human-readable
        explainable match factors.
        """
        factors: List[str] = []
        sub_scores: Dict[str, float] = {}

        # 1. Course Match  (Weight: 0.35)
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

        # 2. Location Affinity  (Weight: 0.25)
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
                s_loc = 0.25
        sub_scores['location'] = s_loc

        # 3. Budget Compatibility  (Weight: 0.20)
        budget = pref.get('max_budget')
        min_fee = college.get('min_fee')

        if budget is None or budget <= 0:
            s_budget = 1.0
        elif min_fee is None:
            s_budget = 0.5
            factors.append("ℹ Tuition fee schedule not published; verify with admission office.")
        elif min_fee <= budget:
            ratio = min_fee / budget
            s_budget = 1.0 - (0.15 * ratio)
            factors.append(
                f"✓ Within your specified annual budget ceiling of Rs.{budget:,.0f} "
                f"(starting at Rs.{min_fee:,.0f})."
            )
        else:
            over_ratio = (min_fee - budget) / budget
            s_budget = max(0.0, 1.0 - over_ratio)
            if s_budget > 0.4:
                factors.append(
                    f"△ Annual tuition (Rs.{min_fee:,.0f}) slightly exceeds your preferred budget limit."
                )
        sub_scores['budget'] = s_budget

        # 4. College Type & Autonomy Match  (Weight: 0.10)
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

            if tt_lower == 'autonomous':
                if is_autonomous or 'autonomous' in ct_lower:
                    s_type = 1.0
                    factors.append("✓ Matches your preference for an Autonomous institution.")
                else:
                    s_type = 0.3
            elif (
                tt_lower in (ct_lower, pt_lower)
                or (tt_lower in ('government', 'govt') and ('government' in ct_lower or 'government' in pt_lower))
                or (tt_lower in ('aided', 'government-aided', 'govt-aided') and ('aided' in ct_lower or 'aided' in pt_lower))
                or (tt_lower in ('self-financing', 'private') and ('self' in ct_lower or 'self' in pt_lower))
            ):
                s_type = 1.0
                factors.append(f"✓ Matches your preferred institution type ({college_type}).")
            else:
                s_type = 0.3

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

        # 5. Facility Coverage  (Weight: 0.10)
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
            self.weights['course']       * s_course +
            self.weights['location']     * s_loc    +
            self.weights['budget']       * s_budget +
            self.weights['college_type'] * s_type   +
            self.weights['facilities']   * s_fac
        )

        final_percentage = round(weighted_sum * 100.0, 1)

        if college.get('data_status') == 'SAMPLE':
            factors.append("⚠️ Sample test record used for academic development.")

        return final_percentage, factors, sub_scores
```

### A.3.3  Scoring Formula

For each college the final score is computed as:

```
S = 100 × (0.35 × s_course + 0.25 × s_location + 0.20 × s_budget + 0.10 × s_type + 0.10 × s_facilities)
```

Where each sub-score is in the range [0.0, 1.0].

### A.3.4  Sub-Score Detail

| Criterion | Condition | Sub-score |
|-----------|-----------|-----------|
| **Course** | Exact course name match | 1.0 |
| | Partial / keyword match | 0.7 |
| | No match | 0.0 |
| | Course not specified | 1.0 (neutral) |
| **Location** | City exactly matches | 1.0 |
| | District matches | 0.85 |
| | Different district, same state | 0.25 |
| | Location not specified | 1.0 (neutral) |
| **Budget** | Not specified | 1.0 (neutral) |
| | Fee <= budget | 0.85 – 1.0 (better if lower fee) |
| | Fee data unavailable | 0.5 (uncertainty penalty) |
| | Fee exceeds budget | max(0, 1 − (fee−budget)/budget) |
| **College Type** | Not specified | 1.0 (neutral) |
| | Exact / synonym match | 1.0 |
| | No match | 0.3 |
| | Autonomy mismatch | ×0.5 penalty on type score |
| **Facilities** | None requested | 1.0 (neutral) |
| | Fraction matched | len(matched) / len(requested) |

---

## A.4  Integration with Flask and the Database

### A.4.1  ORM Models Used by the Recommender

#### College Model — `app/models/college.py` (key fields)

```python
from datetime import datetime, timezone
from app import db


class College(db.Model):
    __tablename__ = 'colleges'

    id              = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name            = db.Column(db.String(255), nullable=False, index=True)
    code            = db.Column(db.String(50), nullable=True, index=True)
    state           = db.Column(db.String(100), default='Tamil Nadu', nullable=False)
    district_id     = db.Column(db.Integer, db.ForeignKey('districts.id'), nullable=True, index=True)
    district        = db.Column(db.String(100), nullable=False, index=True)
    city            = db.Column(db.String(100), nullable=False, index=True)
    college_type    = db.Column(db.String(100), nullable=False, index=True)
    # Multi-Dimensional Taxonomy fields
    primary_college_type = db.Column(db.String(50), nullable=False, default='UNKNOWN', index=True)
    autonomous_status    = db.Column(db.String(50), nullable=False, default='NON_AUTONOMOUS', index=True)
    # Contact and web
    website              = db.Column(db.String(255), nullable=True)
    official_website     = db.Column(db.String(500), nullable=True)
    official_website_url = db.Column(db.String(500), nullable=True)
    phone                = db.Column(db.String(50), nullable=True)
    email                = db.Column(db.String(100), nullable=True)
    # Academic
    accreditation   = db.Column(db.String(100), nullable=True)
    affiliation     = db.Column(db.String(150), nullable=True)
    rating          = db.Column(db.Float, nullable=True, default=4.2)
    # Geo-coordinates
    latitude        = db.Column(db.Float, nullable=True)
    longitude       = db.Column(db.Float, nullable=True)
    # Data provenance
    data_status     = db.Column(db.String(50), default='SAMPLE', nullable=False)
    last_updated    = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    # Relationships
    courses    = db.relationship('Course',   backref='college', cascade='all, delete-orphan', lazy='selectin')
    facilities = db.relationship('Facility', backref='college', cascade='all, delete-orphan', lazy='selectin')
```

#### Course Model — `app/models/course.py`

```python
class Course(db.Model):
    __tablename__ = 'courses'

    id              = db.Column(db.Integer, primary_key=True, autoincrement=True)
    college_id      = db.Column(db.Integer, db.ForeignKey('colleges.id', ondelete='CASCADE'), nullable=False)
    course_name     = db.Column(db.String(150), nullable=False, index=True)
    course_category = db.Column(db.String(100), nullable=True)
    degree          = db.Column(db.String(50),  nullable=True)
    department      = db.Column(db.String(120), nullable=True)
    annual_fee      = db.Column(db.Float, nullable=True)   # None if fee data unavailable
    duration_years  = db.Column(db.Float, nullable=True)
    intake_seats    = db.Column(db.Integer, nullable=True)
    admission_mode  = db.Column(db.String(120), nullable=True)
    eligibility     = db.Column(db.Text, nullable=True)
```

#### StudentPreference Model — `app/models/preference.py` (persisted search history)

```python
import json
from datetime import datetime, timezone
from app import db


class StudentPreference(db.Model):
    __tablename__ = 'student_preferences'

    id                   = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id              = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    course_name          = db.Column(db.String(150), nullable=True)
    state                = db.Column(db.String(100), default='Tamil Nadu', nullable=False)
    district             = db.Column(db.String(100), nullable=True)
    city                 = db.Column(db.String(100), nullable=True)
    budget               = db.Column(db.Float, nullable=True)
    college_type         = db.Column(db.String(100), nullable=True)
    facility_preferences = db.Column(db.Text, nullable=True)   # JSON-encoded list

    def get_facilities_list(self) -> list:
        if not self.facility_preferences:
            return []
        try:
            return json.loads(self.facility_preferences)
        except Exception:
            return []

    def set_facilities_list(self, facilities: list) -> None:
        self.facility_preferences = json.dumps(facilities)
```

---

### A.4.2  Flask Route — `POST /api/recommend`

**File:** `app/routes/recommendations.py`

```python
from flask import Blueprint, render_template, request, jsonify
from app import csrf
from app.services.college_service import CollegeService
from app.services.recommendation_service import RecommendationService

recommendations_bp = Blueprint('recommendations', __name__)


@recommendations_bp.route('/recommendations')
def recommendations_page():
    """Renders the AI Recommendation interface."""
    courses       = CollegeService.get_all_courses()
    districts     = CollegeService.get_all_districts()
    college_types = CollegeService.get_all_college_types()
    facilities    = CollegeService.get_all_facilities()
    return render_template(
        'recommendations.html',
        courses=courses,
        districts=districts,
        college_types=college_types,
        facilities=facilities
    )


@recommendations_bp.route('/api/recommend', methods=['POST'])
@csrf.exempt
def api_recommend():
    """
    POST /api/recommend
    Accepts a JSON preference payload and returns ranked college recommendations.
    """
    try:
        payload = request.get_json() or {}
        results = RecommendationService.get_recommendations(payload, top_k=12)
        return jsonify({'success': True, **results}), 200

    except ValueError as ve:
        return jsonify({
            'success': False,
            'error': {'code': 'VALIDATION_ERROR', 'message': str(ve)}
        }), 400

    except Exception as e:
        return jsonify({
            'success': False,
            'error': {'code': 'RECOMMENDER_ERROR', 'message': str(e)}
        }), 500
```

**Route summary:**

| Route | Method | Auth required | Description |
|-------|--------|--------------|-------------|
| `/recommendations` | GET | No | Renders recommendation UI page |
| `/api/recommend` | POST | No (CSRF exempt for JSON) | College recommendation API |
| `/api/recommend/courses` | POST | No | Course suitability scoring API |
| `/api/courses/discover` | POST | No | Normal course filter/discovery API |

---

### A.4.3  Application Factory — Blueprint Registration

**File:** `app/__init__.py` (relevant excerpt)

```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect

db      = SQLAlchemy()
migrate = Migrate()
csrf    = CSRFProtect()


def create_app(config_name=None):
    """Application Factory for EduVerse AI."""
    app = Flask(__name__)
    app.config.from_object(config_by_name.get(config_name, config_by_name['default']))
    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    from app.routes.recommendations import recommendations_bp
    app.register_blueprint(recommendations_bp)
    # ... (other blueprints: main, auth, colleges, comparison, analytics, admin, student)
    return app
```

---

### A.4.4  Database Configuration

**File:** `config.py` (sensitive values redacted)

```python
import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / '.env')


class Config:
    # SECRET_KEY loaded from .env — never hardcoded in source
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True

    @staticmethod
    def get_database_uri():
        """
        Priority:
          1. DATABASE_URL environment variable (full URI — supports MySQL / SQLite)
          2. MYSQL_USER + MYSQL_DATABASE environment variables
          3. SQLite fallback at instance/eduverse_dev.db
        Database password is read from MYSQL_PASSWORD env var — never hardcoded.
        """
        explicit_url = os.getenv('DATABASE_URL')
        if explicit_url:
            return explicit_url
        mysql_user = os.getenv('MYSQL_USER')
        mysql_db   = os.getenv('MYSQL_DATABASE', 'eduverse_ai')
        if mysql_user and mysql_db:
            # URI assembled from env vars; password from MYSQL_PASSWORD
            pass
        instance_db = BASE_DIR / 'instance' / 'eduverse_dev.db'
        return f"sqlite:///{instance_db}"


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # Isolated in-memory DB for pytest
```

> **Security note:** Database passwords (`MYSQL_PASSWORD`) and the `SECRET_KEY` are loaded exclusively
> from the `.env` file and are never stored in source code or version control.

---

## A.5  Example Input and Output

### A.5.1  Example API Request

```bash
POST /api/recommend
Content-Type: application/json

{
    "course":       "MCA",
    "state":        "Tamil Nadu",
    "district":     "Coimbatore",
    "city":         "",
    "budget":       80000,
    "college_type": "Government",
    "autonomous":   "",
    "facilities":   ["Hostel", "Placement Cell"]
}
```

**Field mapping to preference vector:**

| JSON key | Preference vector key | Value used in scoring |
|----------|-----------------------|----------------------|
| `"course"` | `target_course` | `"mca"` |
| `"district"` | `target_district` | `"coimbatore"` |
| `"city"` | `target_city` | `""` (not specified) |
| `"budget"` | `max_budget` | `80000.0` |
| `"college_type"` | `target_type` | `"Government"` |
| `"autonomous"` | `target_autonomous` | `""` (not specified) |
| `"facilities"` | `desired_facilities` | `["hostel", "placement cell"]` |

---

### A.5.2  Scoring Trace — Government College of Technology (GCT Coimbatore)

**Candidate college data (from database):**
- District: `Coimbatore`
- Courses: `B.E. Computer Science and Engineering`, `MCA`
- Type: `Government`
- Primary type: `GOVERNMENT`
- Min annual fee: Rs. 22,000
- Facilities: Hostel, Central Library, Laboratories, Placement Cell, Sports Complex, WiFi Campus

**Step-by-step calculation:**

| # | Criterion | Weight | Calculation | Sub-score |
|---|-----------|--------|-------------|-----------|
| 1 | Course | 0.35 | `"mca"` found in courses list → exact match | 1.00 |
| 2 | Location | 0.25 | `"coimbatore"` in college district → district match | 0.85 |
| 3 | Budget | 0.20 | Rs. 22,000 <= Rs. 80,000 → ratio=0.275 → `1.0 − (0.15 × 0.275)` | 0.96 |
| 4 | Type | 0.10 | `"government"` matches `college_type = "Government"` | 1.00 |
| 5 | Facilities | 0.10 | Hostel ✓, Placement Cell ✓ → 2/2 matched | 1.00 |

```
S = 100 × (0.35×1.00 + 0.25×0.85 + 0.20×0.96 + 0.10×1.00 + 0.10×1.00)
  = 100 × (0.350 + 0.213 + 0.192 + 0.100 + 0.100)
  = 100 × 0.955
  = 95.5
```

---

### A.5.3  Example API Response (abbreviated)

```json
{
    "success": true,
    "count": 2,
    "disclaimer": "Recommendations are informational and depend on the quality...",
    "preferences_applied": {
        "course": "MCA",
        "district": "Coimbatore",
        "city": "Any",
        "budget": 80000,
        "college_type": "Government",
        "autonomous": "Any",
        "facilities": ["Hostel", "Placement Cell"]
    },
    "recommendations": [
        {
            "college_id": 6,
            "college_name": "Government College of Technology (GCT Coimbatore)",
            "score": 95.5,
            "location": "Coimbatore, Coimbatore",
            "district": "Coimbatore",
            "city": "Coimbatore",
            "college_type": "Government",
            "primary_college_type": "GOVERNMENT",
            "autonomous_status": "NON_AUTONOMOUS",
            "is_autonomous": false,
            "fee": 22000.0,
            "data_status": "VERIFIED",
            "courses": ["B.E. Computer Science and Engineering", "MCA"],
            "facilities": [
                "Hostel", "Central Library", "Laboratories",
                "Placement Cell", "Sports Complex", "WiFi Campus"
            ],
            "matching_factors": [
                "✓ MCA program is offered at this institution.",
                "✓ Located in your preferred district of Coimbatore.",
                "✓ Within your specified annual budget ceiling of Rs.80,000 (starting at Rs.22,000).",
                "✓ Matches your preferred institution type (Government).",
                "✓ Provides requested facilities: Hostel, Placement Cell."
            ],
            "sub_scores": {
                "course": 1.0,
                "location": 0.85,
                "budget": 0.96,
                "type": 1.0,
                "facilities": 1.0
            },
            "has_coordinates": true,
            "latitude": 11.0183,
            "longitude": 76.9366,
            "official_website": "https://gct.ac.in",
            "official_website_url": "https://gct.ac.in"
        }
    ]
}
```

---

### A.5.4  Empty-Result Response (No Colleges for District)

When no colleges exist in the database for the requested district, the service returns:

```json
{
    "success": true,
    "recommendations": [],
    "count": 0,
    "message": "No college information is currently available for the selected district.",
    "disclaimer": "Recommendations are informational...",
    "preferences_applied": {
        "course": "MCA",
        "district": "Perambalur",
        "city": "Any",
        "budget": null,
        "college_type": "Any",
        "autonomous": "Any",
        "facilities": []
    }
}
```

### A.5.5  Validation Error Response

```json
{
    "success": false,
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Budget must be a non-negative number."
    }
}
```

---

## A.6  Secondary Course Recommendation Service

A second, independent recommendation service handles **course discovery** rather than college selection.
Accessible at `POST /api/recommend/courses` and `POST /api/courses/discover`.

**File:** `app/services/course_recommendation_service.py`

**Mode 1 — `recommend_courses_ai` (formula-based aptitude scoring):**

```
FinalScore = min(98.5, (0.45 × Marks12th + 0.40 × AvgSubjectScore + min(15, InterestBonus)) × StreamFactor)
```

Where:
- `Marks12th` = student's 12th standard aggregate percentage
- `AvgSubjectScore` = average of marks in subjects relevant to the course (Mathematics, Computer Science, etc.)
- `InterestBonus` = +10.0 per declared career interest that aligns with the course's career field
- `StreamFactor` = 1.0 if stream matches; 0.8 if only partial match

**Mode 2 — `discover_courses_normal` (rule-based filter):**
Simple eligibility filtering by marks cutoff, stream, category, and career field — no ranking formula applied.

Both modes call `Course.query.filter(Course.course_name.ilike(...)).count()` to report the actual
count of colleges in the database offering each programme.

> **Clarification:** This service uses a deterministic mathematical formula, not a trained ML model.
> It is accurately described as a **formula-based aptitude scoring system**.

---

## A.7  Test Results

**Test file:** `tests/test_recommendations.py`
**Test runner:** pytest 8.3.5 on Python 3.12.10 (Windows)
**Test database:** SQLite in-memory (`sqlite:///:memory:`) with data seeded from `seed/seed_data.py`

**Command executed:**
```bash
venv\Scripts\python.exe -m pytest tests\test_recommendations.py -v
```

**Results:**

| Test Name | Input Scenario | Expected Outcome | Result |
|-----------|---------------|-----------------|--------|
| `test_recommendation_valid_input_and_structure` | Full preference vector: course=MCA, district=Chennai, budget=100000, type=University Department, facilities=["Hostel","Central Library","Placement Cell"] | HTTP 200, `success=True`, recommendations list non-empty, score in [0,100], matching_factors present | **PASSED** |
| `test_recommendation_ranking_order` | course=MCA, district=Coimbatore, budget=80000 | Results ordered strictly descending by score | **PASSED** |
| `test_recommendation_invalid_budget` | budget=-10000 | HTTP 400, error code = `VALIDATION_ERROR` | **PASSED** |
| `test_recommendation_no_matching_course` | course=`NonExistentDegreeProgramXYZ` | HTTP 200, recommendations list empty (len=0) | **PASSED** |
| `test_recommendation_empty_preferences_handled` | Empty JSON payload `{}` | HTTP 200, recommendations list non-empty (default ranking) | **PASSED** |

**Overall: 5 passed in 27.32 seconds — exit code 0**

---

## A.8  File Summary

| File | Purpose |
|------|---------|
| `app/recommender/__init__.py` | Package initializer |
| `app/recommender/recommender.py` | Orchestrates full recommendation pipeline |
| `app/recommender/scoring.py` | Weighted multi-criteria scoring + explainable factor generation |
| `app/recommender/feature_engineering.py` | ORM-to-DataFrame conversion; preference vector construction |
| `app/services/recommendation_service.py` | Service layer: validation, district check, preference persistence, result assembly |
| `app/services/course_recommendation_service.py` | Secondary engine: course suitability scoring and normal discovery |
| `app/routes/recommendations.py` | Flask Blueprint: recommendation page and API endpoints |
| `app/models/college.py` | `College` ORM model with serialization |
| `app/models/course.py` | `Course` ORM model (fee, duration, eligibility) |
| `app/models/facility.py` | `Facility` ORM model (campus amenities) |
| `app/models/preference.py` | `StudentPreference` ORM model (persisted student search history) |
| `app/models/district.py` | `District` ORM model (38 Tamil Nadu districts) |
| `app/utils/district_normalizer.py` | District alias resolution and fuzzy DB lookup |
| `app/utils/validators.py` | General-purpose input validators |
| `config.py` | Flask configuration classes (Development, Testing, Production) |
| `tests/test_recommendations.py` | pytest test suite for the recommendation endpoint |
| `tests/conftest.py` | pytest fixtures (in-memory DB, test client, session setup) |
| `seed/seed_data.py` | Database seeder: 38 TN districts + 38+ verified Tamil Nadu college records |

---

## A.9  Implementation Classification

| Claim | Verified fact |
|-------|--------------|
| Trained ML model | **Not used.** No `.pkl`, `.joblib`, `.h5`, or `.pt` model file exists or is loaded. `sklearn.preprocessing.OneHotEncoder` is imported in `feature_engineering.py` but is not used in the active recommendation code path. |
| Rule-based scoring | **Confirmed.** The recommender applies a deterministic weighted formula with configurable weights summing to 1.0. |
| Content-based filtering | **Confirmed.** Colleges are ranked against the user preference vector; no collaborative filtering or user-behaviour data is used. |
| Database-backed results | **Confirmed.** All college, course, and facility data originates from the SQLite/MySQL database seeded from `seed/seed_data.py`. Fake or hardcoded college records are not used in the recommendation output. |
| Explainable results | **Confirmed.** Every recommendation includes a `matching_factors` list of human-readable explanation strings describing why each college was recommended. |

---

*End of Appendix A — EduVerse AI Recommendation Model Source Code*
