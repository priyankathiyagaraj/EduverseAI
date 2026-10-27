from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, session
from app import db, csrf
from app.models.college import College
from app.models.course import Course
from app.models.district import District
from app.models.student_query import StudentQuery

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    try:
        total_colleges = College.query.count()
        total_courses = Course.query.count()
        total_districts = District.query.count()
        stats = {
            'total_colleges': total_colleges,
            'total_courses': total_courses,
            'total_districts': total_districts if total_districts > 0 else 38,
            'transparency': '100% Sourced'
        }
    except Exception:
        stats = {
            'total_colleges': 1129,
            'total_courses': 8120,
            'total_districts': 38,
            'transparency': '100% Sourced'
        }
    return render_template('index.html', stats=stats)


@main_bp.route('/about', methods=['GET', 'POST'])
def about():
    """
    Renders the premium EduVerse AI About Us page and processes
    student query submissions.
    """
    if request.method == 'POST':
        data = {
            'student_name': request.form.get('student_name', '').strip(),
            'email': request.form.get('email', '').strip(),
            'phone': request.form.get('phone', '').strip(),
            'category': request.form.get('category', '').strip(),
            'message': request.form.get('message', '').strip()
        }

        valid, err = StudentQuery.validate_query_data(data)
        if not valid:
            flash(err, 'error')
            return redirect(url_for('main.about', _anchor='query-section'))

        # Resolve student_id if logged in or registered
        current_u = session.get('user')
        student_id = current_u.get('id') if current_u else None
        if not student_id:
            from app.models.user import User
            matched_user = User.query.filter_by(email=data['email'].lower()).first()
            if matched_user and matched_user.role == 'student':
                student_id = matched_user.id

        query = StudentQuery(
            student_id=student_id,
            student_name=data['student_name'],
            email=data['email'],
            phone=data['phone'] or None,
            category=data['category'],
            message=data['message'],
            status='PENDING'
        )
        db.session.add(query)
        db.session.commit()

        flash(
            f"Thank you, {query.student_name}! Your query (Ticket #{query.id}) has been submitted successfully. "
            "Our administration team will review it and follow up via email.",
            'success'
        )
        return redirect(url_for('main.about', _anchor='query-section'))

    total_colleges = College.query.count()
    total_courses = Course.query.count()
    total_districts = District.query.count()
    verified_websites_count = College.query.filter_by(website_status='VERIFIED').count()

    from app.services.student_analytics_service import get_feedback_analytics
    feedback_stats = get_feedback_analytics()

    return render_template(
        'about.html',
        stats={
            'total_colleges': total_colleges,
            'total_courses': total_courses,
            'total_districts': total_districts,
            'verified_websites': verified_websites_count,
            'avg_rating': feedback_stats.get('avg_rating', 0.0),
            'total_feedback': feedback_stats.get('total_feedback', 0)
        },
        feedback_stats=feedback_stats,
        query_categories=StudentQuery.CATEGORIES
    )


@main_bp.route('/feedback', methods=['POST'])
def submit_feedback():
    """Web form submission for student feedback and ratings."""
    name = request.form.get('student_name', '').strip()
    email = request.form.get('email', '').strip().lower()
    rating = request.form.get('rating')
    message = request.form.get('feedback_message', '').strip()

    from app.models.student_feedback import StudentFeedback
    valid, err = StudentFeedback.validate_feedback_data({
        'student_name': name,
        'email': email,
        'rating': rating,
        'feedback_message': message
    })
    if not valid:
        flash(err, 'error')
        return redirect(url_for('main.about', _anchor='feedback-section'))

    current_u = session.get('user')
    student_id = current_u.get('id') if current_u else None
    if not student_id and email:
        from app.models.user import User
        matched_user = User.query.filter_by(email=email).first()
        if matched_user and matched_user.role == 'student':
            student_id = matched_user.id

    fb = StudentFeedback(
        student_id=student_id,
        student_name=name,
        email=email or None,
        rating=int(rating),
        feedback_message=message or None
    )
    db.session.add(fb)
    db.session.commit()

    flash("Thank you for your rating and feedback! Your voice helps improve EduVerse AI.", "success")
    return redirect(url_for('main.about', _anchor='feedback-section'))


@main_bp.route('/api/feedback', methods=['POST'])
@csrf.exempt
def api_submit_feedback():
    """REST API endpoint for submitting student rating and feedback."""
    data = request.get_json() or {}
    from app.models.student_feedback import StudentFeedback
    valid, err = StudentFeedback.validate_feedback_data(data)
    if not valid:
        return jsonify({
            'success': False,
            'error': {'code': 'VALIDATION_ERROR', 'message': err}
        }), 400

    current_u = session.get('user')
    student_id = current_u.get('id') if current_u else None
    email = (data.get('email') or '').strip().lower()
    if not student_id and email:
        from app.models.user import User
        matched_user = User.query.filter_by(email=email).first()
        if matched_user and matched_user.role == 'student':
            student_id = matched_user.id

    fb = StudentFeedback(
        student_id=student_id,
        student_name=data['student_name'].strip(),
        email=email or None,
        rating=int(data['rating']),
        feedback_message=(data.get('feedback_message') or '').strip() or None
    )
    db.session.add(fb)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'Thank you! Your feedback has been recorded successfully.',
        'feedback': fb.to_dict()
    }), 201


@main_bp.route('/api/queries', methods=['POST'])
@csrf.exempt
def api_submit_query():
    """
    REST API endpoint for submitting student queries.
    Validates input, associates student_id, persists to student_queries table, and returns ticket reference.
    """
    data = request.get_json() or {}
    valid, err = StudentQuery.validate_query_data(data)
    if not valid:
        return jsonify({
            'success': False,
            'error': {'code': 'VALIDATION_ERROR', 'message': err}
        }), 400

    email = data['email'].strip().lower()
    current_u = session.get('user')
    student_id = current_u.get('id') if current_u else None
    if not student_id:
        from app.models.user import User
        matched_user = User.query.filter_by(email=email).first()
        if matched_user and matched_user.role == 'student':
            student_id = matched_user.id

    query = StudentQuery(
        student_id=student_id,
        student_name=data['student_name'].strip(),
        email=email,
        phone=data.get('phone', '').strip() or None,
        category=data['category'].strip(),
        message=data['message'].strip(),
        status='PENDING'
    )
    db.session.add(query)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': f"Your query has been submitted successfully! Reference Ticket: #{query.id}.",
        'query': query.to_dict()
    }), 201


@main_bp.route('/my-queries')
def my_queries():
    """
    Student portal for viewing submitted queries and official administrator responses.
    """
    user_info = session.get('user')
    if not user_info:
        flash("Please log in to view your submitted queries.", "info")
        return redirect(url_for('auth.login_page', next=url_for('main.my_queries')))

    user_id = user_info.get('id')
    user_email = user_info.get('email', '').lower()

    queries = StudentQuery.query.filter(
        db.or_(
            StudentQuery.student_id == user_id,
            StudentQuery.email == user_email
        )
    ).order_by(StudentQuery.created_at.desc()).all()

    return render_template(
        'student/my_queries.html',
        queries=queries,
        student=user_info
    )


@main_bp.route('/api/student/queries', methods=['GET'])
def api_student_queries():
    """REST API endpoint for student's own queries."""
    user_info = session.get('user')
    if not user_info:
        return jsonify({
            'success': False,
            'error': {'code': 'UNAUTHORIZED', 'message': 'Authentication required.'}
        }), 401

    user_id = user_info.get('id')
    user_email = user_info.get('email', '').lower()

    queries = StudentQuery.query.filter(
        db.or_(
            StudentQuery.student_id == user_id,
            StudentQuery.email == user_email
        )
    ).order_by(StudentQuery.created_at.desc()).all()

    return jsonify({
        'success': True,
        'count': len(queries),
        'queries': [q.to_dict() for q in queries]
    }), 200
