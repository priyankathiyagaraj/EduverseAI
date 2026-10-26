from functools import wraps
from flask import session, redirect, url_for, flash, request, jsonify, abort


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            if request.path.startswith('/api/'):
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'UNAUTHORIZED',
                        'message': 'Authentication required to access this resource.'
                    }
                }), 401
            flash('Please sign in to access this page.', 'warning')
            return redirect(url_for('auth.login_page', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = session.get('user')
        if not user or user.get('role') != 'admin':
            if request.path.startswith('/api/'):
                return jsonify({
                    'success': False,
                    'error': {
                        'code': 'FORBIDDEN',
                        'message': 'Administrative privileges required.'
                    }
                }), 403
            abort(403)
        return f(*args, **kwargs)
    return decorated_function
