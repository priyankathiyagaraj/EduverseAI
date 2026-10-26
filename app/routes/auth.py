from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from app import db, csrf
from app.models.user import User
from app.utils.validators import validate_registration_payload, validate_email

auth_bp = Blueprint('auth', __name__)


# ==========================================
# WEB TEMPLATE ROUTES
# ==========================================

@auth_bp.route('/register', methods=['GET', 'POST'])
def register_page():
    if 'user' in session:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')

        if password != confirm:
            flash('Passwords do not match.', 'error')
            return render_template('register.html', name=name, email=email)

        valid, error_msg = validate_registration_payload({'name': name, 'email': email, 'password': password})
        if not valid:
            flash(error_msg, 'error')
            return render_template('register.html', name=name, email=email)

        if User.query.filter_by(email=email).first():
            flash('An account with this email address already exists. Please sign in.', 'error')
            return render_template('register.html', name=name)

        # Create new student account
        user = User(name=name, email=email, role='student')
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        # Set session
        session['user'] = user.to_dict()
        flash(f"Welcome to EduVerse AI, {user.name}!", 'success')
        return redirect(url_for('colleges.explore'))

    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login_page():
    if 'user' in session:
        return redirect(url_for('main.index'))

    next_url = request.args.get('next')

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not email or not password:
            flash('Please enter both email and password.', 'error')
            return render_template('login.html', email=email, next=next_url)

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            flash('Invalid email address or password. Please try again.', 'error')
            return render_template('login.html', email=email, next=next_url)

        # Successfully authenticated
        if user.role == 'student':
            from app.services.student_analytics_service import record_student_login
            activity = record_student_login(user, request)
            if activity:
                session['login_activity_id'] = activity.id

        session['user'] = user.to_dict()
        flash(f"Welcome back, {user.name}!", 'success')

        if next_url and next_url.startswith('/'):
            return redirect(next_url)
        if user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('colleges.explore'))

    return render_template('login.html', next=next_url)


@auth_bp.route('/logout')
def logout():
    user_info = session.get('user')
    activity_id = session.pop('login_activity_id', None)
    if user_info and user_info.get('role') == 'student':
        from app.services.student_analytics_service import record_student_logout
        record_student_logout(user_info.get('id'), activity_id)

    session.pop('user', None)
    flash('You have been signed out successfully.', 'info')
    return redirect(url_for('main.index'))


# ==========================================
# REST API ENDPOINTS
# ==========================================

@auth_bp.route('/api/auth/register', methods=['POST'])
@csrf.exempt
def api_register():
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    valid, error_msg = validate_registration_payload({'name': name, 'email': email, 'password': password})
    if not valid:
        return jsonify({
            'success': False,
            'error': {'code': 'VALIDATION_ERROR', 'message': error_msg}
        }), 400

    if User.query.filter_by(email=email).first():
        return jsonify({
            'success': False,
            'error': {'code': 'DUPLICATE_EMAIL', 'message': 'Email is already registered.'}
        }), 409

    user = User(name=name, email=email, role='student')
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    session['user'] = user.to_dict()

    return jsonify({
        'success': True,
        'message': 'Account registered successfully.',
        'user': user.to_dict()
    }), 201


@auth_bp.route('/api/auth/login', methods=['POST'])
@csrf.exempt
def api_login():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({
            'success': False,
            'error': {'code': 'MISSING_CREDENTIALS', 'message': 'Email and password are required.'}
        }), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({
            'success': False,
            'error': {'code': 'INVALID_CREDENTIALS', 'message': 'Invalid email or password.'}
        }), 401

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


@auth_bp.route('/api/auth/logout', methods=['POST'])
@csrf.exempt
def api_logout():
    user_info = session.get('user')
    activity_id = session.pop('login_activity_id', None)
    if user_info and user_info.get('role') == 'student':
        from app.services.student_analytics_service import record_student_logout
        record_student_logout(user_info.get('id'), activity_id)

    session.pop('user', None)
    return jsonify({
        'success': True,
        'message': 'Logged out successfully.'
    }), 200
