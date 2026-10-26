from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List
from sqlalchemy import func, case
from app import db
from app.models.user import User
from app.models.student_login_activity import StudentLoginActivity
from app.models.student_feedback import StudentFeedback
from app.models.student_query import StudentQuery

# Configurable inactivity timeout (e.g., 30 minutes)
INACTIVITY_TIMEOUT_MINUTES = 30


def get_safe_client_ip(req) -> str:
    """Extracts a privacy-safe IP address from request headers."""
    if not req:
        return '127.0.0.1'
    x_forwarded_for = req.headers.get('X-Forwarded-For')
    if x_forwarded_for:
        # Take the first IP before any proxies
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = req.remote_addr or '127.0.0.1'
    # Truncate if unusually long
    return ip[:45]


def record_student_login(user: User, req=None) -> StudentLoginActivity:
    """
    Records a successful student login in student_login_activity
    and updates the user's last_login_at and last_activity_at.
    Does NOT record logins for administrators.
    """
    if not user or user.role != 'student':
        return None

    now = datetime.now(timezone.utc)
    user.last_login_at = now
    user.last_activity_at = now

    ip = get_safe_client_ip(req) if req else None

    activity = StudentLoginActivity(
        student_id=user.id,
        login_time=now,
        session_status='ACTIVE',
        ip_address=ip
    )
    db.session.add(activity)
    db.session.commit()
    return activity


def record_student_logout(user_id: int, activity_id: int = None) -> None:
    """
    Records student logout time, closes the active session status,
    and resets last_activity_at to None so the student is immediately inactive.
    """
    now = datetime.now(timezone.utc)

    # Reset user's active timestamp
    user = db.session.get(User, user_id)
    if user:
        user.last_activity_at = None

    # Update activity record
    activity = None
    if activity_id:
        activity = db.session.get(StudentLoginActivity, activity_id)

    if not activity and user_id:
        activity = StudentLoginActivity.query.filter_by(
            student_id=user_id,
            session_status='ACTIVE'
        ).order_by(StudentLoginActivity.login_time.desc()).first()

    if activity:
        activity.logout_time = now
        activity.session_status = 'LOGGED_OUT'

    db.session.commit()


def touch_student_activity(user_id: int) -> None:
    """Updates user last_activity_at if user is a student."""
    user = db.session.get(User, user_id)
    if user and user.role == 'student':
        user.last_activity_at = datetime.now(timezone.utc)
        db.session.commit()


def get_student_overview_stats() -> Dict[str, Any]:
    """
    Calculates dynamic overview metrics for the Admin Dashboard.
    All values are computed directly from the live database.
    """
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(minutes=INACTIVITY_TIMEOUT_MINUTES)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_start = now - timedelta(days=7)
    month_start = now - timedelta(days=30)

    # 1. Total Registered Students (Only students, no admins)
    total_students = User.query.filter_by(role='student').count()

    # 2. Currently Active Students (Recent authenticated session within timeout)
    active_students = User.query.filter(
        User.role == 'student',
        User.last_activity_at.isnot(None),
        User.last_activity_at >= cutoff
    ).count()

    # 3. Total Logins (from student_login_activity)
    total_logins = StudentLoginActivity.query.count()
    today_logins = StudentLoginActivity.query.filter(StudentLoginActivity.login_time >= today_start).count()
    week_logins = StudentLoginActivity.query.filter(StudentLoginActivity.login_time >= week_start).count()
    month_logins = StudentLoginActivity.query.filter(StudentLoginActivity.login_time >= month_start).count()

    # 4. Total Feedback
    total_feedback = StudentFeedback.query.count()

    # 5. Queries Status Breakdown
    pending_queries = StudentQuery.query.filter_by(status='PENDING').count()
    in_progress_queries = StudentQuery.query.filter_by(status='IN_PROGRESS').count()
    resolved_queries = StudentQuery.query.filter(
        StudentQuery.status.in_(['RESOLVED', 'CLOSED'])
    ).count()
    total_queries = StudentQuery.query.count()

    # Feedback star breakdown & average rating
    avg_rating_raw = db.session.query(func.avg(StudentFeedback.rating)).scalar()
    avg_rating = round(float(avg_rating_raw), 1) if avg_rating_raw else 0.0

    return {
        'total_students': total_students,
        'active_students': active_students,
        'total_logins': total_logins,
        'today_logins': today_logins,
        'week_logins': week_logins,
        'month_logins': month_logins,
        'total_feedback': total_feedback,
        'avg_rating': avg_rating,
        'pending_queries': pending_queries,
        'in_progress_queries': in_progress_queries,
        'resolved_queries': resolved_queries,
        'total_queries': total_queries,
        'inactivity_timeout_minutes': INACTIVITY_TIMEOUT_MINUTES
    }


def get_login_chart_data(timeframe: str = '7d') -> Dict[str, Any]:
    """
    Returns aggregated login counts by date/period from student_login_activity.
    Timeframes supported: 'today', '7d', '30d'.
    Guarantees pure database values with zero fake or hardcoded numbers.
    """
    now = datetime.now(timezone.utc)
    labels: List[str] = []
    data_points: List[int] = []

    if timeframe == 'today':
        # Hourly breakdown for today (24 hours or past 12 2-hour slots)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        # 4-hour or 2-hour buckets from 00:00 to 24:00
        intervals = [
            ("00:00 - 04:00", 0, 4),
            ("04:00 - 08:00", 4, 8),
            ("08:00 - 12:00", 8, 12),
            ("12:00 - 16:00", 12, 16),
            ("16:00 - 20:00", 16, 20),
            ("20:00 - 24:00", 20, 24)
        ]
        for label, start_h, end_h in intervals:
            b_start = today_start.replace(hour=start_h)
            b_end = today_start.replace(hour=end_h - 1, minute=59, second=59)
            cnt = StudentLoginActivity.query.filter(
                StudentLoginActivity.login_time >= b_start,
                StudentLoginActivity.login_time <= b_end
            ).count()
            labels.append(label)
            data_points.append(cnt)

    elif timeframe == '30d':
        # Last 30 days grouped day by day
        for i in range(29, -1, -1):
            day_dt = now - timedelta(days=i)
            day_start = day_dt.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_dt.replace(hour=23, minute=59, second=59, microsecond=999999)
            cnt = StudentLoginActivity.query.filter(
                StudentLoginActivity.login_time >= day_start,
                StudentLoginActivity.login_time <= day_end
            ).count()
            # E.g. 'Sep 15'
            labels.append(day_dt.strftime('%b %d'))
            data_points.append(cnt)

    else:
        # Default: Last 7 Days (Mon, Tue, Wed, ...)
        for i in range(6, -1, -1):
            day_dt = now - timedelta(days=i)
            day_start = day_dt.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_dt.replace(hour=23, minute=59, second=59, microsecond=999999)
            cnt = StudentLoginActivity.query.filter(
                StudentLoginActivity.login_time >= day_start,
                StudentLoginActivity.login_time <= day_end
            ).count()
            # E.g. 'Mon (Sep 22)'
            labels.append(day_dt.strftime('%a (%b %d)'))
            data_points.append(cnt)

    return {
        'timeframe': timeframe,
        'labels': labels,
        'data': data_points,
        'total': sum(data_points)
    }


def get_feedback_analytics() -> Dict[str, Any]:
    """
    Computes feedback counts, average rating, star rating distribution,
    and recent feedback submissions for admin dashboard.
    """
    total = StudentFeedback.query.count()
    avg_rating_raw = db.session.query(func.avg(StudentFeedback.rating)).scalar()
    avg_rating = round(float(avg_rating_raw), 1) if avg_rating_raw else 0.0

    # Star distribution
    star_counts = {
        5: StudentFeedback.query.filter_by(rating=5).count(),
        4: StudentFeedback.query.filter_by(rating=4).count(),
        3: StudentFeedback.query.filter_by(rating=3).count(),
        2: StudentFeedback.query.filter_by(rating=2).count(),
        1: StudentFeedback.query.filter_by(rating=1).count()
    }

    star_percentages = {}
    for star, count in star_counts.items():
        star_percentages[star] = round((count / total * 100), 1) if total > 0 else 0.0

    recent_feedback = StudentFeedback.query.order_by(
        StudentFeedback.created_at.desc()
    ).limit(10).all()

    return {
        'total_feedback': total,
        'avg_rating': avg_rating,
        'star_counts': star_counts,
        'star_percentages': star_percentages,
        'recent_feedback': [f.to_dict() for f in recent_feedback]
    }
