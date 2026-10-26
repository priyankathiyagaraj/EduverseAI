import pytest
from datetime import datetime, timezone, timedelta
from app import db
from app.models.user import User
from app.models.student_login_activity import StudentLoginActivity
from app.models.student_feedback import StudentFeedback
from app.models.student_query import StudentQuery
from app.services.student_analytics_service import (
    record_student_login,
    record_student_logout,
    get_student_overview_stats,
    get_login_chart_data,
    get_feedback_analytics,
    INACTIVITY_TIMEOUT_MINUTES
)


def test_student_login_activity_tracking(app, client):
    """Verifies student login creates an activity record, while admin and failed logins do not."""
    with app.app_context():
        # Clean existing activities
        StudentLoginActivity.query.delete()
        db.session.commit()

        # 1. Failed login does NOT create login activity
        res = client.post('/api/auth/login', json={
            'email': 'student@eduverse.ac.in',
            'password': 'wrongpassword'
        })
        assert res.status_code == 401
        assert StudentLoginActivity.query.count() == 0

        # 2. Admin login does NOT create student login activity
        res = client.post('/api/auth/login', json={
            'email': 'admin@eduverse.ac.in',
            'password': 'Admin@123'
        })
        assert res.status_code == 200
        assert StudentLoginActivity.query.count() == 0

        # 3. Successful student login creates activity record
        res = client.post('/api/auth/login', json={
            'email': 'student@eduverse.ac.in',
            'password': 'Student@123'
        })
        assert res.status_code == 200
        assert StudentLoginActivity.query.count() == 1

        activity = StudentLoginActivity.query.first()
        student = User.query.filter_by(email='student@eduverse.ac.in').first()
        assert activity.student_id == student.id
        assert activity.session_status == 'ACTIVE'
        assert activity.login_time is not None
        assert activity.logout_time is None
        assert student.last_login_at is not None
        assert student.last_activity_at is not None


def test_student_logout_lifecycle(app, client):
    """Verifies that logging out marks session_status as LOGGED_OUT and clears active status."""
    with app.app_context():
        # Login as student
        res_login = client.post('/api/auth/login', json={
            'email': 'student@eduverse.ac.in',
            'password': 'Student@123'
        })
        assert res_login.status_code == 200
        student = User.query.filter_by(email='student@eduverse.ac.in').first()
        assert student.last_activity_at is not None
        activity = StudentLoginActivity.query.filter_by(student_id=student.id).first()
        assert activity.session_status == 'ACTIVE'

        # Logout
        res = client.post('/api/auth/logout')
        assert res.status_code == 200

        # Re-fetch from DB
        db.session.refresh(student)
        db.session.refresh(activity)
        assert activity.session_status == 'LOGGED_OUT'
        assert activity.logout_time is not None
        assert student.last_activity_at is None


def test_active_students_inactivity_window(app):
    """Verifies active students are calculated accurately within the inactivity threshold."""
    with app.app_context():
        now = datetime.now(timezone.utc)

        # Create two test students
        s1 = User(name='Active Student', email='active1@eduverse.ac.in', role='student')
        s1.set_password('TestPass123!')
        s1.last_activity_at = now - timedelta(minutes=5)  # Within 30 min -> ACTIVE

        s2 = User(name='Idle Student', email='idle2@eduverse.ac.in', role='student')
        s2.set_password('TestPass123!')
        s2.last_activity_at = now - timedelta(minutes=45)  # Older than 30 min -> INACTIVE

        s3 = User(name='Offline Student', email='offline3@eduverse.ac.in', role='student')
        s3.set_password('TestPass123!')
        s3.last_activity_at = None  # None -> INACTIVE

        admin = User.query.filter_by(role='admin').first()
        admin.last_activity_at = now  # Admin should NOT be counted as student!

        db.session.add_all([s1, s2, s3])
        db.session.commit()

        stats = get_student_overview_stats()
        # Ensure only student accounts are in total_students
        students_count = User.query.filter_by(role='student').count()
        assert stats['total_students'] == students_count

        # s1 should be active, s2, s3 and admin should NOT be counted
        cutoff = now - timedelta(minutes=INACTIVITY_TIMEOUT_MINUTES)
        expected_active = User.query.filter(
            User.role == 'student',
            User.last_activity_at.isnot(None),
            User.last_activity_at >= cutoff
        ).count()
        assert stats['active_students'] == expected_active
        assert stats['active_students'] >= 1


def test_login_chart_analytics_aggregation(app):
    """Verifies get_login_chart_data returns real counts aggregated from student_login_activity."""
    with app.app_context():
        student = User.query.filter_by(role='student').first()
        now = datetime.now(timezone.utc)

        # Seed login activity records over various days
        StudentLoginActivity.query.delete()
        a1 = StudentLoginActivity(student_id=student.id, login_time=now, session_status='ACTIVE')
        a2 = StudentLoginActivity(student_id=student.id, login_time=now - timedelta(days=1), session_status='LOGGED_OUT')
        a3 = StudentLoginActivity(student_id=student.id, login_time=now - timedelta(days=2), session_status='LOGGED_OUT')
        db.session.add_all([a1, a2, a3])
        db.session.commit()

        chart_7d = get_login_chart_data('7d')
        assert chart_7d['timeframe'] == '7d'
        assert len(chart_7d['labels']) == 7
        assert len(chart_7d['data']) == 7
        assert chart_7d['total'] == 3

        chart_30d = get_login_chart_data('30d')
        assert len(chart_30d['labels']) == 30
        assert chart_30d['total'] == 3


def test_feedback_submission_and_analytics(app, client):
    """Tests feedback submission, validation, and database analytics calculation."""
    with app.app_context():
        StudentFeedback.query.delete()
        db.session.commit()

        # 1. Invalid rating validation
        res = client.post('/api/feedback', json={
            'student_name': 'Rahul K',
            'rating': 6,
            'feedback_message': 'Great'
        })
        assert res.status_code == 400

        # 2. Valid feedback submissions
        res1 = client.post('/api/feedback', json={
            'student_name': 'Priyanka S',
            'email': 'priyanka@gmail.com',
            'rating': 5,
            'feedback_message': 'Very useful college discovery platform!'
        })
        assert res1.status_code == 201

        res2 = client.post('/api/feedback', json={
            'student_name': 'Rahul V',
            'email': 'rahul@gmail.com',
            'rating': 4,
            'feedback_message': 'Good platform and accurate cutoffs.'
        })
        assert res2.status_code == 201

        res3 = client.post('/api/feedback', json={
            'student_name': 'Arun M',
            'rating': 5
        })
        assert res3.status_code == 201

        # 3. Analytics verification
        analytics = get_feedback_analytics()
        assert analytics['total_feedback'] == 3
        # Ratings: 5, 4, 5 -> avg = (14 / 3) = 4.7
        assert analytics['avg_rating'] == 4.7
        assert analytics['star_counts'][5] == 2
        assert analytics['star_counts'][4] == 1
        assert analytics['star_counts'][3] == 0


def test_student_query_flow_and_my_queries(app, client, admin_client):
    """
    Tests complete query lifecycle:
    Student submits query -> Stored with student_id -> Admin responds -> Student sees response in My Queries.
    """
    with app.app_context():
        student = User.query.filter_by(role='student').first()
        student_id = student.id
        student_email = student.email

        # 1. Authenticate as student and submit query
        with client.session_transaction() as sess:
            sess['user'] = student.to_dict()

        res = client.post('/api/queries', json={
            'student_name': 'Anand R',
            'email': student_email,
            'category': 'Course Information',
            'message': 'I need guidance regarding MCA counseling and top autonomous colleges in Chennai.'
        })
        assert res.status_code == 201
        data = res.get_json()
        ticket_id = data['query']['id']

        # Verify student_id was linked in database
        saved_q = db.session.get(StudentQuery, ticket_id)
        assert saved_q.student_id == student_id
        assert saved_q.status == 'PENDING'
        assert saved_q.admin_response is None

        # 2. Student views "My Queries" before response
        res_mq = client.get('/my-queries')
        assert res_mq.status_code == 200
        assert f"Ticket #{ticket_id}" in res_mq.get_data(as_text=True)
        assert "Pending Review" in res_mq.get_data(as_text=True)

        # 3. Admin responds to the query
        admin = User.query.filter_by(role='admin').first()
        with admin_client.session_transaction() as sess:
            sess['user'] = admin.to_dict()

        res_resp = admin_client.post(f'/admin/queries/{ticket_id}/respond', data={
            'admin_response': 'Top autonomous MCA colleges in Chennai include Loyola College, MCC, and Anna University CEG. Counseling starts next month.',
            'status': 'RESOLVED'
        }, follow_redirects=True)
        assert res_resp.status_code == 200

        # Verify DB updated
        db.session.refresh(saved_q)
        assert saved_q.status == 'RESOLVED'
        assert 'Loyola College' in saved_q.admin_response

        # 4. Student views "My Queries" and sees the official response
        with client.session_transaction() as sess:
            sess['user'] = student.to_dict()

        res_mq_updated = client.get('/my-queries')
        assert res_mq_updated.status_code == 200
        html = res_mq_updated.get_data(as_text=True)
        assert "Official EduVerse AI Administrator Response" in html
        assert "Top autonomous MCA colleges in Chennai" in html
        assert "Resolved" in html


def test_admin_dashboard_renders_student_overview_and_chart(admin_client):
    """Verifies Admin Dashboard renders the Student Overview cards and login activity chart container."""
    res = admin_client.get('/admin')
    assert res.status_code == 200
    html = res.get_data(as_text=True)
    assert "Student Overview" in html
    assert "Total Students" in html
    assert "Active Students" in html
    assert "Total Logins" in html
    assert "Total Feedback" in html
    assert "Student Login Activity" in html
    assert "studentLoginChart" in html
    assert "Recent Student Feedback" in html


def test_admin_queries_page_tabs_and_filters(admin_client):
    """Verifies Admin Queries page supports tabs for queries and feedback, and status filtering."""
    # Queries Tab
    res_q = admin_client.get('/admin/queries?tab=queries&status=PENDING')
    assert res_q.status_code == 200
    assert "Student Inquiries Log" in res_q.get_data(as_text=True)

    # Feedback Tab
    res_fb = admin_client.get('/admin/queries?tab=feedback')
    assert res_fb.status_code == 200
    assert "Student Ratings & Comments" in res_fb.get_data(as_text=True)


def test_security_student_blocked_from_admin_analytics(student_client, client):
    """Verifies that unauthenticated users and students cannot access admin analytics or APIs."""
    # 1. Unauthenticated blocked
    assert client.get('/admin').status_code in (302, 401, 403)
    assert client.get('/api/admin/student-overview').status_code in (401, 403)
    assert client.get('/api/admin/analytics/logins').status_code in (401, 403)

    # 2. Student blocked with 403
    assert student_client.get('/admin').status_code == 403
    assert student_client.get('/admin/queries').status_code == 403
    assert student_client.get('/api/admin/student-overview').status_code == 403
    assert student_client.get('/api/admin/analytics/logins').status_code == 403
    assert student_client.get('/api/admin/feedback').status_code == 403
