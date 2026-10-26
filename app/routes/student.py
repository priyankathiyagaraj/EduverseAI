from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from app import db, csrf
from app.models.user import User
from app.models.student_profile import StudentProfile
from app.models.student_query import StudentQuery
from app.services.assessment_service import AssessmentService
from app.services.ai_counselor_service import AICounselorService
from app.services.college_service import CollegeService
from app.utils.validators import validate_registration_payload

student_bp = Blueprint('student', __name__)


# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def get_or_create_student_profile(user_id=None):
    """Retrieves an existing StudentProfile or initializes a new record."""
    if user_id:
        profile = StudentProfile.query.filter_by(user_id=user_id).first()
        if not profile:
            profile = StudentProfile(user_id=user_id)
            db.session.add(profile)
            db.session.commit()
        return profile
    return None


def make_compact_assessment_session(result: dict) -> dict:
    """Creates a lightweight session payload to prevent cookie bloat."""
    if not result:
        return {}
    return {
        'academic': result.get('academic', {}),
        'academic_summary': result.get('academic_summary', {}),
        'recommended_courses': [
            {
                'course_name': c.get('course_name'),
                'category': c.get('category'),
                'suitability_score': c.get('suitability_score'),
                'match_score': c.get('match_score'),
                'stream': c.get('stream', 'Science'),
                'rationale': c.get('rationale', ''),
                'duration': c.get('duration', '3 Years')
            }
            for c in result.get('recommended_courses', [])[:6]
        ],
        'matched_colleges': [
            {
                'id': col.get('id'),
                'name': col.get('name'),
                'district': col.get('district'),
                'college_type': col.get('college_type'),
                'affiliation': col.get('affiliation'),
                'official_website': col.get('official_website')
            }
            for col in result.get('matched_colleges', [])[:6]
        ],
        'career_pathways': result.get('career_pathways', {})
    }


# ==============================================================================
# WEB TEMPLATE ROUTES
# ==============================================================================

@student_bp.route('/student/dashboard')
def dashboard():
    """
    Student Central Dashboard:
    Displays student academic overview, stream, cutoff, recent assessment summary,
    and direct shortcuts to recommendations, official college websites, and AI Counselor.
    """
    user_info = session.get('user')
    profile = None
    recent_result = None

    if user_info:
        profile = StudentProfile.query.filter_by(user_id=user_info.get('id')).first()
        if profile:
            recent_result = profile.get_assessment_result()

    if not recent_result:
        recent_result = session.get('latest_assessment')

    return render_template(
        'student/dashboard.html',
        profile=profile,
        assessment=recent_result,
        streams=AssessmentService.STREAMS,
        interests=AssessmentService.AVAILABLE_INTERESTS
    )


@student_bp.route('/student/profile', methods=['GET', 'POST'])
def profile():
    """
    Student Profile Management:
    Allows students to maintain contact details, 12th stream, school, and preferences.
    """
    user_info = session.get('user')
    if not user_info:
        flash('Please sign in to access your student profile.', 'info')
        return redirect(url_for('auth.login_page', next='/student/profile'))

    user = db.session.get(User, user_info.get('id'))
    if not user:
        session.pop('user', None)
        return redirect(url_for('auth.login_page'))

    profile = get_or_create_student_profile(user.id)
    districts = CollegeService.get_all_districts()

    if request.method == 'POST':
        # Update personal & academic profile fields
        profile.phone = request.form.get('phone', '').strip()
        profile.location = request.form.get('location', '').strip()
        profile.school = request.form.get('school', '').strip()
        profile.stream = request.form.get('stream', '').strip()
        profile.preferred_course = request.form.get('preferred_course', '').strip()
        profile.preferred_district = request.form.get('preferred_district', '').strip()
        profile.college_preference = request.form.get('college_preference', '').strip()
        profile.career_interest = request.form.get('career_interest', '').strip()

        # Update user name if altered
        name = request.form.get('name', '').strip()
        if name and name != user.name:
            user.name = name
            session['user'] = user.to_dict()

        try:
            db.session.commit()
            flash('Your profile has been successfully updated.', 'success')
        except Exception:
            db.session.rollback()
            flash('An error occurred while saving your profile. Please try again.', 'error')

        return redirect(url_for('student.profile'))

    return render_template(
        'student/profile.html',
        user=user,
        profile=profile,
        districts=districts,
        streams=AssessmentService.STREAMS
    )


@student_bp.route('/student/assessment', methods=['GET', 'POST'])
def assessment():
    """
    Interactive 12th Standard Assessment & Guidance Form:
    Captures stream, subject marks, TNEA cutoff calculation, interest ranking,
    and generates tailored course, college, and career recommendations.
    """
    user_info = session.get('user')
    profile = None
    if user_info:
        profile = StudentProfile.query.filter_by(user_id=user_info.get('id')).first()

    districts = CollegeService.get_all_districts()

    if request.method == 'POST':
        # Extract inputs from form
        stream = request.form.get('stream', 'Science').strip()
        subject_names = request.form.getlist('subject_name[]')
        subject_marks = request.form.getlist('subject_mark[]')
        interests = request.form.getlist('interests[]')
        preferred_district = request.form.get('preferred_district', '').strip()
        college_preference = request.form.get('college_preference', 'all').strip()
        career_interest = request.form.get('career_interest', '').strip()

        # Handle max fee budget
        raw_budget = request.form.get('budget_max', '').strip()
        budget_max = float(raw_budget) if raw_budget and raw_budget.replace('.', '', 1).isdigit() else None

        # Assemble subject marks dictionary
        marks_dict = {}
        for s_name, s_mark in zip(subject_names, subject_marks):
            if s_name and s_mark:
                try:
                    num = float(s_mark)
                    marks_dict[s_name.strip()] = num
                except ValueError:
                    continue

        # Build payload for AssessmentService
        eval_payload = {
            'stream': stream,
            'subject_marks': marks_dict,
            'interests': interests,
            'preferred_district': preferred_district,
            'college_preference': college_preference,
            'budget_max': budget_max,
            'career_interest': career_interest
        }

        # Run multi-layered evaluation engine
        assessment_result = AssessmentService.evaluate_student_assessment(eval_payload)

        # Store in session for results view
        session['latest_assessment'] = make_compact_assessment_session(assessment_result)

        # If user is authenticated, persist assessment in database
        if user_info:
            profile = get_or_create_student_profile(user_info.get('id'))
            profile.stream = stream
            profile.set_subject_marks(marks_dict)
            profile.total_marks = assessment_result.get('academic', {}).get('total_marks')
            profile.percentage = assessment_result.get('academic', {}).get('percentage')
            profile.tnea_cutoff = assessment_result.get('academic', {}).get('tnea_cutoff', {}).get('formula_cutoff')
            profile.set_interests(interests)
            profile.preferred_district = preferred_district
            profile.college_preference = college_preference
            profile.career_interest = career_interest
            profile.set_assessment_result(assessment_result)
            try:
                db.session.commit()
            except Exception:
                db.session.rollback()

        return redirect(url_for('student.results'))

    return render_template(
        'student/assessment.html',
        streams=AssessmentService.STREAMS,
        interests=AssessmentService.AVAILABLE_INTERESTS,
        districts=districts,
        profile=profile
    )


@student_bp.route('/student/results')
def results():
    """
    Assessment Report View:
    Displays calculated percentage, TNEA cutoff breakdown, top course recommendations,
    matched Tamil Nadu colleges with official websites, and career pathway outlook.
    """
    assessment_data = session.get('latest_assessment')

    # If session is empty, attempt to read from logged in student's profile
    if not assessment_data:
        user_info = session.get('user')
        if user_info:
            profile = StudentProfile.query.filter_by(user_id=user_info.get('id')).first()
            if profile:
                assessment_data = profile.get_assessment_result()

    if not assessment_data:
        flash('Please complete your 12th standard assessment first to generate recommendations.', 'info')
        return redirect(url_for('student.assessment'))

    return render_template('student/results.html', assessment=assessment_data)


@student_bp.route('/student/careers')
def careers():
    """
    Dedicated Career Pathways & Higher Studies Guide:
    Provides structured breakdowns for popular undergraduate degrees,
    industry job roles, required technical skills, and higher study options (MCA, MBA, etc.).
    """
    catalog = AssessmentService.COURSE_GUIDANCE_CATALOG
    selected_course = request.args.get('course', '').strip()

    return render_template(
        'student/careers.html',
        catalog=catalog,
        selected_course=selected_course
    )


@student_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    """
    Contact Us & Project Team Information Page:
    Showcases project development team (MCA Department, R. Priyadharshini, T. Priyanka)
    and enables students to submit real queries managed in the Admin Dashboard.
    """
    user_info = session.get('user')
    initial_name = user_info.get('name', '') if user_info else ''
    initial_email = user_info.get('email', '') if user_info else ''

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        category = request.form.get('category', 'Course Information').strip()
        message = request.form.get('message', '').strip()

        if not name or not email or not message:
            flash('Please fill in your name, email address, and message.', 'error')
            return render_template(
                'contact.html',
                name=name,
                email=email,
                phone=phone,
                category=category,
                message=message,
                categories=StudentQuery.CATEGORIES
            )

        # Create persistent query record visible in Admin Dashboard
        query_record = StudentQuery(
            student_id=user_info.get('id') if user_info else None,
            student_name=name,
            email=email,
            phone=phone if phone else None,
            category=category if category in StudentQuery.CATEGORIES else 'Course Information',
            message=message,
            status='PENDING'
        )

        try:
            db.session.add(query_record)
            db.session.commit()
            flash('Thank you! Your query has been submitted successfully. Our team will review and respond soon.', 'success')
            return redirect(url_for('student.contact'))
        except Exception:
            db.session.rollback()
            flash('An error occurred while submitting your message. Please try again.', 'error')

    return render_template(
        'contact.html',
        name=initial_name,
        email=initial_email,
        categories=StudentQuery.CATEGORIES
    )


# ==============================================================================
# REST API ENDPOINTS
# ==============================================================================

@student_bp.route('/api/register', methods=['POST'])
@csrf.exempt
def api_register_alias():
    """Direct alias for API student registration."""
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    valid, error_msg = validate_registration_payload({'name': name, 'email': email, 'password': password})
    if not valid:
        return jsonify({'success': False, 'error': {'code': 'VALIDATION_ERROR', 'message': error_msg}}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'success': False, 'error': {'code': 'DUPLICATE_EMAIL', 'message': 'Email is already registered.'}}), 409

    user = User(name=name, email=email, role='student')
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    # Initialize empty student profile
    profile = StudentProfile(user_id=user.id)
    db.session.add(profile)
    db.session.commit()

    session['user'] = user.to_dict()

    return jsonify({
        'success': True,
        'message': 'Student registered successfully.',
        'user': user.to_dict()
    }), 201


@student_bp.route('/api/login', methods=['POST'])
@csrf.exempt
def api_login_alias():
    """Direct alias for API student login."""
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'success': False, 'error': {'code': 'MISSING_FIELDS', 'message': 'Email and password required.'}}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({'success': False, 'error': {'code': 'INVALID_CREDENTIALS', 'message': 'Invalid email or password.'}}), 401

    if user.role == 'student':
        from app.services.student_analytics_service import record_student_login
        activity = record_student_login(user, request)
        if activity:
            session['login_activity_id'] = activity.id

    session['user'] = user.to_dict()

    return jsonify({
        'success': True,
        'message': 'Logged in successfully.',
        'user': user.to_dict()
    }), 200


@student_bp.route('/api/profile', methods=['GET', 'POST'])
@csrf.exempt
def api_profile():
    """Returns or updates the active student's academic and preference profile."""
    user_info = session.get('user')
    if not user_info:
        return jsonify({'success': False, 'error': {'code': 'UNAUTHORIZED', 'message': 'Authentication required.'}}), 401

    profile = get_or_create_student_profile(user_info.get('id'))

    if request.method == 'POST':
        data = request.get_json() or {}
        if 'phone' in data:
            profile.phone = str(data['phone']).strip()
        if 'location' in data:
            profile.location = str(data['location']).strip()
        if 'school' in data:
            profile.school = str(data['school']).strip()
        if 'stream' in data:
            profile.stream = str(data['stream']).strip()
        if 'preferred_course' in data:
            profile.preferred_course = str(data['preferred_course']).strip()
        if 'preferred_district' in data:
            profile.preferred_district = str(data['preferred_district']).strip()
        if 'college_preference' in data:
            profile.college_preference = str(data['college_preference']).strip()
        if 'career_interest' in data:
            profile.career_interest = str(data['career_interest']).strip()
        if 'interests' in data and isinstance(data['interests'], list):
            profile.set_interests(data['interests'])
        if 'subject_marks' in data and isinstance(data['subject_marks'], dict):
            profile.set_subject_marks(data['subject_marks'])

        try:
            db.session.commit()
            return jsonify({'success': True, 'message': 'Profile updated successfully.', 'data': profile.to_dict()}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': {'code': 'SAVE_ERROR', 'message': str(e)}}), 500

    return jsonify({'success': True, 'data': profile.to_dict()}), 200


@student_bp.route('/api/assessment', methods=['POST'])
@csrf.exempt
def api_assessment():
    """
    REST API for running the 12th evaluation engine:
    Calculates percentage, TNEA cutoff, course matches, colleges, and career pathways.
    """
    payload = request.get_json() or {}
    result = AssessmentService.evaluate_student_assessment(payload)

    # Persist if user is logged in
    user_info = session.get('user')
    if user_info:
        profile = get_or_create_student_profile(user_info.get('id'))
        profile.stream = payload.get('stream')
        profile.set_subject_marks(payload.get('subject_marks') or {})
        profile.total_marks = result.get('academic', {}).get('total_marks')
        profile.percentage = result.get('academic', {}).get('percentage')
        profile.tnea_cutoff = result.get('academic', {}).get('tnea_cutoff', {}).get('formula_cutoff')
        profile.set_interests(payload.get('interests') or [])
        profile.preferred_district = payload.get('preferred_district')
        profile.college_preference = payload.get('college_preference')
        profile.career_interest = payload.get('career_interest')
        profile.set_assessment_result(result)
        try:
            db.session.commit()
        except Exception:
            db.session.rollback()

    session['latest_assessment'] = make_compact_assessment_session(result)
    return jsonify({'success': True, 'data': result}), 200


@student_bp.route('/api/recommendations', methods=['POST'])
@csrf.exempt
def api_recommendations():
    """
    Returns filtered college recommendations based on student preferences and marks.
    """
    payload = request.get_json() or {}
    result = AssessmentService.evaluate_student_assessment(payload)
    return jsonify({
        'success': True,
        'academic': result.get('academic'),
        'recommended_courses': result.get('recommended_courses'),
        'matched_colleges': result.get('matched_colleges'),
        'career_pathways': result.get('career_pathways')
    }), 200


@student_bp.route('/api/ai/advisor', methods=['POST'])
@csrf.exempt
def api_ai_advisor():
    """
    AI Counselor Endpoint:
    Accepts student prompt and academic context, returns counseling response
    via Google Gemini API (or rule-based fallback).
    """
    data = request.get_json() or {}
    user_message = (data.get('message') or data.get('query') or '').strip()
    student_context = data.get('context')

    # If context not passed, try to infer from session or user profile
    if not student_context:
        student_context = session.get('latest_assessment')
        if not student_context:
            user_info = session.get('user')
            if user_info:
                profile = StudentProfile.query.filter_by(user_id=user_info.get('id')).first()
                if profile:
                    student_context = profile.to_dict()

    guidance = AICounselorService.get_counselor_response(user_message, student_context)
    return jsonify(guidance), 200
