from typing import Dict, Any, List, Optional
import math
from app.models.course import Course
from app.models.college import College


class CourseRecommendationService:
    """
    Intelligent Course Recommendation & Discovery Engine.
    Provides two distinct approaches:
    1. AI-Powered Course Recommendation: Multi-criteria aptitude scoring based on 12th marks,
       subject proficiency vectors, and career affinity.
    2. Normal Course Discovery: Transparent, rule-based filtering using marks and student preferences.
    """

    # Comprehensive profile of cataloged courses in EduVerse AI
    COURSE_PROFILES = [
        {
            'name': 'B.Tech AI & ML',
            'degree': 'B.Tech',
            'stream_req': ['Science (Maths)', 'Science (CS)', 'Any'],
            'min_percentage': 50.0,
            'core_subjects': ['mathematics', 'computer_science', 'physics'],
            'category': 'Engineering',
            'duration': '4 Years',
            'career_field': 'Software & AI',
            'description': 'Advanced computing combining machine learning algorithms, deep neural architectures, and intelligent systems design.'
        },
        {
            'name': 'B.Tech Data Science',
            'degree': 'B.Tech',
            'stream_req': ['Science (Maths)', 'Science (CS)', 'Any'],
            'min_percentage': 50.0,
            'core_subjects': ['mathematics', 'computer_science', 'statistics'],
            'category': 'Engineering',
            'duration': '4 Years',
            'career_field': 'Software & AI',
            'description': 'Specialized curriculum in predictive modeling, big data analytics, and computational statistics.'
        },
        {
            'name': 'B.Tech Cyber Security',
            'degree': 'B.Tech',
            'stream_req': ['Science (Maths)', 'Science (CS)', 'Any'],
            'min_percentage': 50.0,
            'core_subjects': ['mathematics', 'computer_science', 'physics'],
            'category': 'Engineering',
            'duration': '4 Years',
            'career_field': 'Cybersecurity & Infrastructure',
            'description': 'Network defense, cryptographic protocols, digital forensics, and secure enterprise infrastructure.'
        },
        {
            'name': 'B.E. Computer Science and Engineering',
            'degree': 'B.E.',
            'stream_req': ['Science (Maths)', 'Science (CS)', 'Any'],
            'min_percentage': 45.0,
            'core_subjects': ['mathematics', 'physics', 'computer_science'],
            'category': 'Engineering',
            'duration': '4 Years',
            'career_field': 'Computer Engineering',
            'description': 'Foundational engineering program covering computer architecture, operating systems, and distributed computing.'
        },
        {
            'name': 'B.Tech Information Technology',
            'degree': 'B.Tech',
            'stream_req': ['Science (Maths)', 'Science (CS)', 'Any'],
            'min_percentage': 45.0,
            'core_subjects': ['mathematics', 'physics', 'computer_science'],
            'category': 'Engineering',
            'duration': '4 Years',
            'career_field': 'Information Technology',
            'description': 'Software architecture, database administration, cloud computing, and enterprise application development.'
        },
        {
            'name': 'BCA AI & ML',
            'degree': 'BCA',
            'stream_req': ['Science (Maths)', 'Science (CS)', 'Commerce (Maths)', 'Any'],
            'min_percentage': 45.0,
            'core_subjects': ['mathematics', 'computer_science'],
            'category': 'Computing & IT',
            'duration': '3 Years',
            'career_field': 'Software & AI',
            'description': 'Application-centric bachelor program focused on Python programming, computer vision, and applied ML models.'
        },
        {
            'name': 'BCA Data Science',
            'degree': 'BCA',
            'stream_req': ['Science (Maths)', 'Science (CS)', 'Commerce (Maths)', 'Any'],
            'min_percentage': 45.0,
            'core_subjects': ['mathematics', 'computer_science'],
            'category': 'Computing & IT',
            'duration': '3 Years',
            'career_field': 'Data & Analytics',
            'description': 'Practical data handling, SQL databases, business intelligence, and introductory machine learning.'
        },
        {
            'name': 'BCA',
            'degree': 'BCA',
            'stream_req': ['Any'],
            'min_percentage': 40.0,
            'core_subjects': ['computer_science', 'mathematics'],
            'category': 'Computing & IT',
            'duration': '3 Years',
            'career_field': 'Software Development',
            'description': 'Undergraduate computing qualification emphasizing web development, database systems, and object-oriented programming.'
        },
        {
            'name': 'B.Sc Computer Science',
            'degree': 'B.Sc',
            'stream_req': ['Science (Maths)', 'Science (CS)', 'Any'],
            'min_percentage': 45.0,
            'core_subjects': ['mathematics', 'computer_science', 'physics'],
            'category': 'Computing & IT',
            'duration': '3 Years',
            'career_field': 'Computer Science',
            'description': 'Rigorous theoretical foundations in computational theory, algorithm analysis, and software engineering.'
        },
        {
            'name': 'B.Sc IT',
            'degree': 'B.Sc',
            'stream_req': ['Science (Maths)', 'Science (CS)', 'Any'],
            'min_percentage': 40.0,
            'core_subjects': ['mathematics', 'computer_science'],
            'category': 'Computing & IT',
            'duration': '3 Years',
            'career_field': 'Information Technology',
            'description': 'Network management, web technologies, and systems maintenance.'
        },
        {
            'name': 'B.Com',
            'degree': 'B.Com',
            'stream_req': ['Commerce', 'Commerce (Maths)', 'Any'],
            'min_percentage': 40.0,
            'core_subjects': ['commerce', 'accountancy', 'economics'],
            'category': 'Commerce & Finance',
            'duration': '3 Years',
            'career_field': 'Finance & Accounting',
            'description': 'Comprehensive business finance, taxation laws, auditing standards, and corporate accounting.'
        },
        {
            'name': 'BBA',
            'degree': 'BBA',
            'stream_req': ['Any'],
            'min_percentage': 40.0,
            'core_subjects': ['commerce', 'english', 'economics'],
            'category': 'Management & Business',
            'duration': '3 Years',
            'career_field': 'Business Management',
            'description': 'Business administration, operations management, organizational behavior, and marketing strategies.'
        },
        {
            'name': 'MCA',
            'degree': 'MCA',
            'stream_req': ['Any with BCA / B.Sc CS / Maths at 10+2'],
            'min_percentage': 50.0,
            'core_subjects': ['mathematics', 'computer_science'],
            'category': 'Postgraduate',
            'duration': '2 Years',
            'career_field': 'Software Engineering',
            'description': 'Master of Computer Applications for advanced software engineering, cloud systems, and enterprise design.'
        },
        {
            'name': 'MBA',
            'degree': 'MBA',
            'stream_req': ['Any Undergraduate Degree'],
            'min_percentage': 50.0,
            'core_subjects': ['business', 'quantitative_aptitude'],
            'category': 'Postgraduate',
            'duration': '2 Years',
            'career_field': 'Executive Leadership',
            'description': 'Master of Business Administration for strategic decision making, marketing, operations, and finance leadership.'
        },
        {
            'name': 'M.Sc Computer Science',
            'degree': 'M.Sc',
            'stream_req': ['B.Sc CS / BCA'],
            'min_percentage': 50.0,
            'core_subjects': ['computer_science', 'mathematics'],
            'category': 'Postgraduate',
            'duration': '2 Years',
            'career_field': 'Research & AI',
            'description': 'Advanced academic computing, research methodologies, distributed algorithms, and specialized machine learning.'
        },
        {
            'name': 'M.Com',
            'degree': 'M.Com',
            'stream_req': ['B.Com / BBA'],
            'min_percentage': 50.0,
            'core_subjects': ['commerce', 'accountancy'],
            'category': 'Postgraduate',
            'duration': '2 Years',
            'career_field': 'Finance & Banking',
            'description': 'Postgraduate commerce program covering financial markets, corporate taxation, and portfolio management.'
        }
    ]

    @staticmethod
    def _get_college_count_for_course(course_name: str) -> int:
        """Counts how many institutions in Tamil Nadu offer this course."""
        return Course.query.filter(Course.course_name.ilike(f"%{course_name}%")).count()

    @staticmethod
    def recommend_courses_ai(payload: Dict[str, Any], top_k: int = 6) -> Dict[str, Any]:
        """
        AI-based course recommendation logic.
        Analyzes 12th marks, subject-wise performance, stream, and declared interests.
        Returns explainable match scores without fake claims.
        """
        raw_marks = payload.get('marks_12th')
        if raw_marks is None or raw_marks == '':
            raise ValueError("12th standard aggregate percentage is required.")

        try:
            marks = float(raw_marks)
            if not (0.0 <= marks <= 100.0):
                raise ValueError("Marks must be between 0 and 100 percent.")
        except ValueError:
            raise ValueError("Invalid numerical marks provided.")

        stream = (payload.get('stream') or 'Any').strip()
        interests = payload.get('interests') or []
        if isinstance(interests, str):
            interests = [i.strip() for i in interests.split(',') if i.strip()]

        subject_marks = payload.get('subject_marks') or {}
        maths = float(subject_marks.get('mathematics', marks))
        cs = float(subject_marks.get('computer_science', marks))
        physics = float(subject_marks.get('physics', marks))
        commerce = float(subject_marks.get('commerce', marks))
        accountancy = float(subject_marks.get('accountancy', marks))

        ranked_courses = []

        for profile in CourseRecommendationService.COURSE_PROFILES:
            # 1. Eligibility Check
            is_eligible = marks >= profile['min_percentage']
            if not is_eligible:
                continue

            # 2. Stream affinity
            stream_match = False
            if 'Any' in profile['stream_req']:
                stream_match = True
            elif stream in profile['stream_req']:
                stream_match = True
            elif 'Science' in stream and any('Science' in req for req in profile['stream_req']):
                stream_match = True
            elif 'Commerce' in stream and any('Commerce' in req for req in profile['stream_req']):
                stream_match = True

            # 3. Subject Aptitude Vector Score
            aptitude_scores = []
            factors = []

            for subj in profile['core_subjects']:
                if subj == 'mathematics':
                    aptitude_scores.append(maths)
                    if maths >= 75:
                        factors.append(f"Strong Mathematics score ({maths:.0f}%) fulfills computational requirements.")
                elif subj == 'computer_science':
                    aptitude_scores.append(cs)
                    if cs >= 75:
                        factors.append(f"High Computer Science marks ({cs:.0f}%) indicate programming aptitude.")
                elif subj == 'physics':
                    aptitude_scores.append(physics)
                elif subj == 'commerce':
                    aptitude_scores.append(commerce)
                    if commerce >= 75:
                        factors.append(f"Exemplary Commerce marks ({commerce:.0f}%) align with business curricula.")
                elif subj == 'accountancy':
                    aptitude_scores.append(accountancy)
                    if accountancy >= 75:
                        factors.append(f"Strong Accountancy marks ({accountancy:.0f}%) match financial analytical tracks.")

            avg_aptitude = sum(aptitude_scores) / len(aptitude_scores) if aptitude_scores else marks

            # 4. Interest Alignment Bonus
            interest_bonus = 0.0
            if interests:
                for interest in interests:
                    i_lower = interest.lower()
                    if profile['career_field'].lower() in i_lower or any(word in i_lower for word in profile['name'].lower().split()):
                        interest_bonus += 10.0
                        factors.append(f"Direct alignment with your selected interest: '{interest}'.")
                        break

            # 5. Composite Match Score (0 - 100)
            # Weights: 45% Aggregate Marks, 40% Subject Aptitude, 15% Interest/Stream alignment
            stream_factor = 1.0 if stream_match else 0.8
            base_score = (0.45 * marks) + (0.40 * avg_aptitude) + min(15.0, interest_bonus)
            final_score = round(min(98.5, base_score * stream_factor), 1)

            if not factors:
                factors.append(f"Academic percentage of {marks:.0f}% comfortably exceeds the {profile['min_percentage']:.0f}% cutoff.")

            # Count institutions in DB offering this program
            offering_count = CourseRecommendationService._get_college_count_for_course(profile['name'])

            ranked_courses.append({
                'course_name': profile['name'],
                'degree': profile['degree'],
                'category': profile['category'],
                'duration': profile['duration'],
                'career_field': profile['career_field'],
                'match_score': final_score,
                'min_percentage': profile['min_percentage'],
                'description': profile['description'],
                'matching_factors': factors[:3],
                'colleges_available_count': offering_count,
                'explore_url': f"/explore?course={profile['name']}"
            })

        # Sort descending by match score
        ranked_courses.sort(key=lambda x: x['match_score'], reverse=True)

        return {
            'mode': 'AI_POWERED',
            'student_summary': {
                'marks_12th': marks,
                'stream': stream,
                'interests': interests
            },
            'count': len(ranked_courses[:top_k]),
            'courses': ranked_courses[:top_k],
            'algorithm_explanation': (
                "Recommendations are computed by evaluating your 12th marks against official Tamil Nadu eligibility thresholds, "
                "synthesized with a subject-weighted aptitude vector and declared career preferences."
            )
        }

    @staticmethod
    def discover_courses_normal(payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normal, filter-driven course discovery.
        Does NOT apply predictive AI ranking; allows students to filter by stream, minimum cutoff, and field.
        """
        raw_marks = payload.get('marks_12th')
        marks = float(raw_marks) if raw_marks and str(raw_marks).replace('.', '', 1).isdigit() else None
        stream = (payload.get('stream') or '').strip()
        category = (payload.get('category') or '').strip()
        career_field = (payload.get('career_field') or '').strip()

        matching_courses = []

        for profile in CourseRecommendationService.COURSE_PROFILES:
            # Marks eligibility filter
            if marks is not None and marks < profile['min_percentage']:
                continue

            # Stream filter
            if stream and stream != 'Any':
                if 'Any' not in profile['stream_req'] and stream not in profile['stream_req']:
                    if not (('Science' in stream and any('Science' in req for req in profile['stream_req'])) or
                            ('Commerce' in stream and any('Commerce' in req for req in profile['stream_req']))):
                        continue

            # Category filter
            if category and category != 'All' and profile['category'] != category:
                continue

            # Career field filter
            if career_field and career_field != 'All' and career_field.lower() not in profile['career_field'].lower():
                continue

            offering_count = CourseRecommendationService._get_college_count_for_course(profile['name'])

            matching_courses.append({
                'course_name': profile['name'],
                'degree': profile['degree'],
                'category': profile['category'],
                'duration': profile['duration'],
                'career_field': profile['career_field'],
                'min_percentage': profile['min_percentage'],
                'description': profile['description'],
                'colleges_available_count': offering_count,
                'explore_url': f"/explore?course={profile['name']}"
            })

        return {
            'mode': 'NORMAL_DISCOVERY',
            'filters_applied': {
                'marks_12th': marks,
                'stream': stream or 'Any',
                'category': category or 'All',
                'career_field': career_field or 'All'
            },
            'count': len(matching_courses),
            'courses': matching_courses
        }
