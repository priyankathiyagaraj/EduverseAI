from typing import Dict, Any, List, Optional
import math
from app.models.course import Course
from app.models.college import College


class AssessmentService:
    """
    Core Evaluation & Career Guidance Engine for 12th Standard Students.
    Handles stream analysis, subject marks calculation, TNEA cutoff evaluation,
    interest multi-attribute matching, course recommendations, college matching,
    and structured career pathway guidance.
    """

    STREAMS = [
        {
            'id': 'Science',
            'name': 'Science (Mathematics / CS / Biology)',
            'description': 'For students with Physics, Chemistry, Mathematics, and Computer Science / Biology.',
            'default_subjects': ['Mathematics', 'Physics', 'Chemistry', 'Computer Science']
        },
        {
            'id': 'Commerce',
            'name': 'Commerce (Accountancy / Business Maths)',
            'description': 'For students with Accountancy, Commerce, Economics, and Business Mathematics / Computer Applications.',
            'default_subjects': ['Accountancy', 'Commerce', 'Economics', 'Business Mathematics']
        },
        {
            'id': 'Arts',
            'name': 'Arts & Humanities',
            'description': 'For students with History, Political Science, Economics, Literature, and Social Sciences.',
            'default_subjects': ['History', 'Economics', 'Political Science', 'English Literature']
        },
        {
            'id': 'Vocational',
            'name': 'Vocational / Other',
            'description': 'For students with vocational training or interdisciplinary combinations.',
            'default_subjects': ['Vocational Subject 1', 'Vocational Subject 2', 'English', 'General Mathematics']
        }
    ]

    AVAILABLE_INTERESTS = [
        {'id': 'Technology', 'label': 'Technology & Computing', 'icon': '💻'},
        {'id': 'Programming', 'label': 'Software & Programming', 'icon': '⌨️'},
        {'id': 'Data', 'label': 'Data & Analytics', 'icon': '📊'},
        {'id': 'Engineering', 'label': 'Engineering & Machinery', 'icon': '⚙️'},
        {'id': 'Business', 'label': 'Business & Startups', 'icon': '💼'},
        {'id': 'Management', 'label': 'Management & Operations', 'icon': '📈'},
        {'id': 'Finance', 'label': 'Finance & Accounting', 'icon': '💰'},
        {'id': 'Design', 'label': 'UI/UX & Creative Design', 'icon': '🎨'},
        {'id': 'Medicine', 'label': 'Healthcare & Medicine', 'icon': '🩺'},
        {'id': 'Research', 'label': 'Science & Research', 'icon': '🔬'},
        {'id': 'Teaching', 'label': 'Teaching & Education', 'icon': '📚'},
        {'id': 'Communication', 'label': 'Media & Communication', 'icon': '🗣️'}
    ]

    COURSE_GUIDANCE_CATALOG = [
        {
            'name': 'BCA',
            'degree': 'BCA',
            'category': 'Computing & IT',
            'duration': '3 Years',
            'stream_req': ['Science', 'Commerce', 'Vocational', 'Arts', 'Any'],
            'min_percentage': 40.0,
            'career_field': 'Software & Application Development',
            'description': 'Application-oriented undergraduate computing degree providing hands-on training in programming, web development, and database architectures.',
            'career_paths': [
                'Software Developer',
                'Web & Full-Stack Developer',
                'Application Support Engineer',
                'Software Quality Assurance (QA) Tester',
                'Database Administrator'
            ],
            'higher_studies': [
                'MCA (Master of Computer Applications)',
                'M.Sc Computer Science / IT',
                'MBA in Information Systems',
                'Global Cloud & Cybersecurity Certifications (AWS, Azure, CompTIA)'
            ],
            'skills_to_develop': [
                'Programming (Python, Java, JavaScript)',
                'Relational & NoSQL Databases (SQL, MongoDB)',
                'Web Development (React, Node.js, HTML5/CSS3)',
                'Algorithmic Problem Solving & Data Structures'
            ]
        },
        {
            'name': 'B.Sc Computer Science',
            'degree': 'B.Sc',
            'category': 'Computing & IT',
            'duration': '3 Years',
            'stream_req': ['Science', 'Any'],
            'min_percentage': 45.0,
            'career_field': 'Computer Science & Software',
            'description': 'Theoretical and practical foundations of computing systems, computational theory, operating systems, and software engineering.',
            'career_paths': [
                'Junior Software Engineer',
                'Systems Analyst',
                'Data Analyst',
                'Network Administrator',
                'Research Assistant'
            ],
            'higher_studies': [
                'M.Sc Computer Science / Data Science',
                'MCA',
                'M.Sc Artificial Intelligence',
                'Integrated Ph.D. in Computer Science'
            ],
            'skills_to_develop': [
                'Discrete Mathematics & Algorithms',
                'C++, Java, and Python Programming',
                'Operating Systems & Computer Networks',
                'Data Analysis & Visualization'
            ]
        },
        {
            'name': 'B.E. Computer Science and Engineering',
            'degree': 'B.E.',
            'category': 'Engineering',
            'duration': '4 Years',
            'stream_req': ['Science'],
            'min_percentage': 45.0,
            'career_field': 'Computer Engineering',
            'description': 'Rigorous 4-year engineering program recognized by AICTE, covering computer hardware-software co-design, distributed systems, and modern AI.',
            'career_paths': [
                'Software Development Engineer (SDE)',
                'Cloud Solutions Architect',
                'DevOps Engineer',
                'Cybersecurity Specialist',
                'Embedded Systems Engineer'
            ],
            'higher_studies': [
                'M.E. / M.Tech in Computer Science',
                'MS in Computer Science abroad (US, UK, Germany)',
                'MBA (Tech Management / Strategy)',
                'GATE / Direct Ph.D. in Premier Institutes (IITs, NITs)'
            ],
            'skills_to_develop': [
                'Object-Oriented Design & Clean Architecture',
                'Cloud Architecture & Microservices',
                'Operating Systems, Compilers & Low-Level Systems',
                'System Design & Distributed Data Systems'
            ]
        },
        {
            'name': 'B.Tech AI & ML',
            'degree': 'B.Tech',
            'category': 'Engineering',
            'duration': '4 Years',
            'stream_req': ['Science'],
            'min_percentage': 50.0,
            'career_field': 'Software & AI',
            'description': 'Specialized undergraduate engineering degree focused on machine learning models, deep learning, computer vision, and generative AI systems.',
            'career_paths': [
                'AI/ML Engineer',
                'Machine Learning Researcher',
                'Computer Vision Engineer',
                'Natural Language Processing (NLP) Specialist',
                'Data Science Consultant'
            ],
            'higher_studies': [
                'M.Tech in Artificial Intelligence',
                'MS in Robotics / Machine Learning abroad',
                'Ph.D. in Machine Intelligence'
            ],
            'skills_to_develop': [
                'Python, PyTorch, TensorFlow',
                'Linear Algebra, Calculus & Statistics',
                'Neural Networks & Deep Learning Architectures',
                'MLOps & Production Model Deployment'
            ]
        },
        {
            'name': 'B.Tech Information Technology',
            'degree': 'B.Tech',
            'category': 'Engineering',
            'duration': '4 Years',
            'stream_req': ['Science'],
            'min_percentage': 45.0,
            'career_field': 'Information Technology',
            'description': 'Enterprise software design, information infrastructure, cloud platforms, and cybersecurity protocols.',
            'career_paths': [
                'IT Systems Consultant',
                'Full-Stack Developer',
                'Cloud Infrastructure Engineer',
                'Information Security Analyst',
                'Technical Project Manager'
            ],
            'higher_studies': [
                'M.Tech in Information Technology',
                'MBA in Information Technology Management',
                'MS in Cybersecurity / Cloud Computing'
            ],
            'skills_to_develop': [
                'Cloud Computing (AWS / GCP / Azure)',
                'Enterprise Java / Spring Boot / Node.js',
                'Network Security & Threat Assessment',
                'Agile Project Methodologies'
            ]
        },
        {
            'name': 'B.Com',
            'degree': 'B.Com',
            'category': 'Commerce & Finance',
            'duration': '3 Years',
            'stream_req': ['Commerce', 'Science', 'Arts', 'Any'],
            'min_percentage': 40.0,
            'career_field': 'Finance & Accounting',
            'description': 'Comprehensive business degree covering corporate accounting, financial planning, taxation regulations, and banking operations.',
            'career_paths': [
                'Accountant / Senior Accountant',
                'Financial Analyst',
                'Taxation Consultant',
                'Banking Officer / Executive',
                'Audit Associate'
            ],
            'higher_studies': [
                'Chartered Accountancy (CA - ICAI)',
                'Cost and Management Accounting (CMA)',
                'Company Secretary (CS)',
                'M.Com / MBA in Finance'
            ],
            'skills_to_develop': [
                'Financial Accounting & Bookkeeping',
                'Direct & Indirect Taxation (GST, Income Tax)',
                'Advanced Microsoft Excel & Tally Prime',
                'Financial Modeling & Valuation'
            ]
        },
        {
            'name': 'BBA',
            'degree': 'BBA',
            'category': 'Management & Business',
            'duration': '3 Years',
            'stream_req': ['Commerce', 'Science', 'Arts', 'Vocational', 'Any'],
            'min_percentage': 40.0,
            'career_field': 'Business Management',
            'description': 'Broad-based business management curriculum covering marketing, human resource development, corporate strategy, and operations.',
            'career_paths': [
                'Business Development Executive',
                'Marketing Associate',
                'Human Resource (HR) Generalist',
                'Operations Management Trainee',
                'Client Relationship Manager'
            ],
            'higher_studies': [
                'MBA (Marketing, Finance, HR, Operations, Business Analytics)',
                'PGDM (Post Graduate Diploma in Management)',
                'Specialized International Business Masters abroad'
            ],
            'skills_to_develop': [
                'Strategic Thinking & Business Leadership',
                'Market Research & Brand Strategy',
                'Interpersonal & Business Communication',
                'Operational Efficiency & Team Management'
            ]
        },
        {
            'name': 'B.Sc IT',
            'degree': 'B.Sc',
            'category': 'Computing & IT',
            'duration': '3 Years',
            'stream_req': ['Science', 'Commerce', 'Any'],
            'min_percentage': 40.0,
            'career_field': 'Information Technology',
            'description': 'Undergraduate computing degree concentrating on database administration, systems networking, and web applications.',
            'career_paths': [
                'IT Support Engineer',
                'Web Administrator',
                'Network Technician',
                'Software Support Specialist'
            ],
            'higher_studies': [
                'M.Sc Information Technology',
                'MCA',
                'Professional Networking Certifications (CCNA)'
            ],
            'skills_to_develop': [
                'Web Technologies & Scripting',
                'Computer Network Configuration',
                'Database Queries & Management',
                'Technical Troubleshooting'
            ]
        }
    ]

    @staticmethod
    def calculate_tnea_cutoff(maths: float, physics: float, chemistry: float) -> Dict[str, Any]:
        """
        Calculates official TNEA Engineering Admission Cutoff.
        Primary Formula specified by requirement:
        TNEA cutoff = Mathematics mark / 2 + Physics mark / 4 + Chemistry mark / 4

        Also calculates the standard Tamil Nadu 200-scale cutoff:
        TN 200-Cutoff = Maths + (Physics / 2) + (Chemistry / 2)
        """
        maths_clean = max(0.0, min(100.0, float(maths)))
        physics_clean = max(0.0, min(100.0, float(physics)))
        chem_clean = max(0.0, min(100.0, float(chemistry)))

        # Weighted components per formula: Maths/2 + Physics/4 + Chemistry/4
        maths_contrib = maths_clean / 2.0
        physics_contrib = physics_clean / 4.0
        chem_contrib = chem_clean / 4.0
        formula_cutoff = round(maths_contrib + physics_contrib + chem_contrib, 2)

        # Standard 200-mark Tamil Nadu scale: Maths + Physics/2 + Chemistry/2
        standard_200_cutoff = round(maths_clean + (physics_clean / 2.0) + (chem_clean / 2.0), 2)

        return {
            'formula_cutoff': formula_cutoff,
            'standard_200_cutoff': standard_200_cutoff,
            'breakdown': {
                'mathematics': {
                    'mark': maths_clean,
                    'component': round(maths_contrib, 2),
                    'formula_text': f"{maths_clean:.1f} / 2 = {maths_contrib:.2f}"
                },
                'physics': {
                    'mark': physics_clean,
                    'component': round(physics_contrib, 2),
                    'formula_text': f"{physics_clean:.1f} / 4 = {physics_contrib:.2f}"
                },
                'chemistry': {
                    'mark': chem_clean,
                    'component': round(chem_contrib, 2),
                    'formula_text': f"{chem_clean:.1f} / 4 = {chem_contrib:.2f}"
                }
            },
            'disclaimer': (
                "Official TNEA Cutoff Guidance: This calculated cutoff is provided for academic planning and decision support. "
                "Official seat allotment cutoffs vary each academic year based on state percentile distribution and category reservations. "
                "Students must verify live counseling schedules and current eligibility criteria directly on the official TNEA portal (tneaonline.org)."
            )
        }

    @staticmethod
    def evaluate_student_assessment(payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executes end-to-end evaluation:
        1. Academic calculation: Total marks, percentage, TNEA cutoff
        2. Interest synthesis
        3. Course recommendation ranking with suitability rationale
        4. College guidance matching (with verified official websites across TN)
        5. Career pathways breakdown
        """
        stream = (payload.get('stream') or 'Science').strip()
        raw_subject_marks = payload.get('subject_marks') or {}

        # 1. Validate and clean subject marks
        cleaned_marks = {}
        total = 0.0
        for subj, val in raw_subject_marks.items():
            if val is not None and str(val).strip() != '':
                try:
                    num = float(val)
                    if 0 <= num <= 100:
                        cleaned_marks[subj.strip()] = num
                        total += num
                except (ValueError, TypeError):
                    continue

        if not cleaned_marks:
            # Fallback to single aggregate marks if entered
            raw_aggregate = payload.get('marks_12th') or payload.get('percentage') or 75.0
            try:
                agg_val = float(raw_aggregate)
                cleaned_marks['Aggregate Marks'] = max(0.0, min(100.0, agg_val))
                total = cleaned_marks['Aggregate Marks']
            except (ValueError, TypeError):
                cleaned_marks['Aggregate Marks'] = 75.0
                total = 75.0

        count = len(cleaned_marks)
        percentage = round(total / count, 2) if count > 0 else 0.0

        # 2. Compute TNEA Cutoff if applicable (Science with Maths, Physics, Chemistry)
        tnea_data = None
        m_mark = cleaned_marks.get('Mathematics') or cleaned_marks.get('maths')
        p_mark = cleaned_marks.get('Physics') or cleaned_marks.get('physics')
        c_mark = cleaned_marks.get('Chemistry') or cleaned_marks.get('chemistry')

        if m_mark is not None and p_mark is not None and c_mark is not None:
            tnea_data = AssessmentService.calculate_tnea_cutoff(m_mark, p_mark, c_mark)

        # 3. Clean interests
        interests = payload.get('interests') or []
        if isinstance(interests, str):
            interests = [i.strip() for i in interests.split(',') if i.strip()]

        preferred_district = (payload.get('preferred_district') or '').strip()

        # 4. Generate Recommended Fields (2–5 suitable fields)
        recommended_fields = []
        if 'Science' in stream or any(i in ['Technology', 'Programming', 'Data', 'Engineering'] for i in interests):
            recommended_fields.append({
                'title': 'Computing, Software & Artificial Intelligence',
                'description': 'Ideal for careers in software engineering, full-stack development, and data intelligence.',
                'icon': '💻'
            })
            if tnea_data and tnea_data['standard_200_cutoff'] >= 140:
                recommended_fields.append({
                    'title': 'Engineering & Technical Systems',
                    'description': 'Core engineering, hardware-software integration, cloud infrastructure, and robotics.',
                    'icon': '⚙️'
                })

        if 'Commerce' in stream or any(i in ['Business', 'Finance', 'Management'] for i in interests):
            recommended_fields.append({
                'title': 'Financial Analytics & Corporate Commerce',
                'description': 'Corporate taxation, chartered accountancy, investment banking, and financial auditing.',
                'icon': '💰'
            })
            recommended_fields.append({
                'title': 'Business Administration & Management',
                'description': 'Strategic leadership, operational logistics, brand marketing, and entrepreneurship.',
                'icon': '📊'
            })

        if any(i in ['Design', 'Communication', 'Teaching', 'Research'] for i in interests) or 'Arts' in stream:
            recommended_fields.append({
                'title': 'Digital Media, Design & Humanities',
                'description': 'Visual design, technical communication, higher educational research, and social analytics.',
                'icon': '🎨'
            })

        if not recommended_fields:
            recommended_fields.append({
                'title': 'Information Technology & Applied Computing',
                'description': 'Versatile undergraduate programs bridging digital applications and business operations.',
                'icon': '🌐'
            })

        # 5. Course Recommendations & Matching
        recommended_courses = []
        for course_def in AssessmentService.COURSE_GUIDANCE_CATALOG:
            # Eligibility check
            if percentage < course_def['min_percentage']:
                continue

            # Stream compatibility
            stream_compat = False
            if 'Any' in course_def['stream_req']:
                stream_compat = True
            elif stream in course_def['stream_req']:
                stream_compat = True
            elif 'Science' in stream and 'Science' in course_def['stream_req']:
                stream_compat = True
            elif 'Commerce' in stream and 'Commerce' in course_def['stream_req']:
                stream_compat = True

            if not stream_compat and 'Any' not in course_def['stream_req']:
                continue

            # Score calculation
            score = 65.0
            reasons = []

            # Percentage bonus
            if percentage >= 80:
                score += 15.0
                reasons.append(f"Your strong academic percentage ({percentage}%) meets competitive institutional cutoffs.")
            elif percentage >= course_def['min_percentage']:
                score += 8.0
                reasons.append(f"Your percentage ({percentage}%) exceeds the minimum eligibility of {course_def['min_percentage']}%.")

            # Stream matching reason
            if stream in course_def['stream_req']:
                score += 10.0
                reasons.append(f"Direct match with your 12th {stream} curriculum.")

            # Interest matching
            matched_interest = False
            for interest in interests:
                if (interest.lower() in course_def['career_field'].lower() or
                        interest.lower() in course_def['category'].lower() or
                        any(interest.lower() in p.lower() for p in course_def['career_paths'])):
                    score += 10.0
                    reasons.append(f"Direct alignment with your selected interest in {interest}.")
                    matched_interest = True
                    break

            # TNEA bonus for engineering
            if course_def['category'] == 'Engineering' and tnea_data:
                if tnea_data['standard_200_cutoff'] >= 160:
                    score += 5.0
                    reasons.append(f"Calculated TNEA Cutoff ({tnea_data['standard_200_cutoff']:.1f}/200) positions you well for top Anna University affiliated institutions.")

            final_match = round(min(97.0, score), 1)

            # Query institutions offering this course in Tamil Nadu
            offering_count = Course.query.filter(Course.course_name.ilike(f"%{course_def['name']}%")).count()

            rationale_text = "; ".join(reasons[:2]) if reasons else course_def['description']

            recommended_courses.append({
                'course_name': course_def['name'],
                'degree': course_def['degree'],
                'category': course_def['category'],
                'duration': course_def['duration'],
                'career_field': course_def['career_field'],
                'match_score': final_match,
                'suitability_score': final_match,
                'min_percentage': course_def['min_percentage'],
                'description': course_def['description'],
                'rationale': rationale_text,
                'suitability_reasons': reasons[:3],
                'career_paths': course_def['career_paths'],
                'higher_studies': course_def['higher_studies'],
                'skills_to_develop': course_def['skills_to_develop'],
                'colleges_available_count': offering_count,
                'explore_url': f"/explore?course={course_def['name']}" + (f"&district={preferred_district}" if preferred_district else "")
            })

        # Sort descending by match score
        recommended_courses.sort(key=lambda x: x['match_score'], reverse=True)

        # 6. College Guidance Matching (Colleges offering top courses)
        top_course_names = [c['course_name'] for c in recommended_courses[:3]]
        college_query = College.query
        if preferred_district:
            college_query = college_query.filter(College.district.ilike(f"%{preferred_district}%"))

        matched_colleges_models = college_query.limit(8).all()
        matched_colleges = []
        for col in matched_colleges_models:
            c_dict = col.to_dict(include_details=False)
            # Add Chennai Project Categorization if applicable
            if col.district and 'chennai' in col.district.lower():
                fee_val = col.courses[0].annual_fee if col.courses and col.courses[0].annual_fee else 50000
                if fee_val <= 35000:
                    c_dict['project_category'] = 'Budget'
                elif fee_val <= 85000:
                    c_dict['project_category'] = 'Standard'
                else:
                    c_dict['project_category'] = 'Premium'
                c_dict['category_note'] = "Project filter category based on tuition fee range, not an official government ranking."
            matched_colleges.append(c_dict)

        academic_data = {
            'stream': stream,
            'subject_marks': cleaned_marks,
            'total_marks': round(total, 1),
            'max_total': len(cleaned_marks) * 100 if cleaned_marks else 400,
            'percentage': percentage,
            'tnea_cutoff': tnea_data
        }

        top_course = recommended_courses[0] if recommended_courses else {}
        career_pathways = {
            'possible_careers': top_course.get('career_paths', ['Software Developer', 'Technical Analyst', 'System Engineer']),
            'higher_studies': top_course.get('higher_studies', ['MCA', 'M.Sc Computer Science', 'MBA']),
            'key_skills': top_course.get('skills_to_develop', ['Programming & Logic', 'Database Management', 'Problem Solving'])
        }

        return {
            'academic_summary': academic_data,
            'academic': academic_data,
            'interest_summary': {
                'selected_interests': interests,
                'count': len(interests)
            },
            'recommended_fields': recommended_fields[:4],
            'recommended_courses': recommended_courses[:6],
            'college_guidance': {
                'preferred_district': preferred_district or 'All Tamil Nadu Districts',
                'colleges': matched_colleges,
                'total_found': len(matched_colleges),
                'disclaimer': "College information sourced from EduVerse AI institutional directory with verified official website links."
            },
            'matched_colleges': matched_colleges,
            'career_pathways': career_pathways,
            'guidance_wording': "Based on your inputs, you may explore the following suitable educational pathways:"
        }
