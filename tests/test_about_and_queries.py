import pytest
from app import db
from app.models.student_query import StudentQuery
from app.models.user import User


def test_student_query_model_validation():
    """Verify StudentQuery validation logic for required fields and formats."""
    # 1. Valid data
    valid_data = {
        'student_name': 'Priyanka S',
        'email': 'priyanka@gmail.com',
        'phone': '+91 9876543210',
        'category': 'Course Information',
        'message': 'Which course is suitable for my 12th marks in computer science?'
    }
    is_valid, err = StudentQuery.validate_query_data(valid_data)
    assert is_valid is True
    assert err is None

    # 2. Invalid Email
    invalid_email = valid_data.copy()
    invalid_email['email'] = 'not-an-email'
    is_valid, err = StudentQuery.validate_query_data(invalid_email)
    assert is_valid is False
    assert "valid email" in err.lower()

    # 3. Short Message (< 10 chars)
    short_msg = valid_data.copy()
    short_msg['message'] = 'Hi'
    is_valid, err = StudentQuery.validate_query_data(short_msg)
    assert is_valid is False
    assert "at least 10 characters" in err.lower()

    # 4. Invalid Category
    bad_cat = valid_data.copy()
    bad_cat['category'] = 'Unrecognized Category'
    is_valid, err = StudentQuery.validate_query_data(bad_cat)
    assert is_valid is False
    assert "invalid category" in err.lower()


def test_about_page_renders_all_required_sections(client):
    """Verify that the About Us page renders properly with all mandatory sections and forms."""
    res = client.get('/about')
    assert res.status_code == 200
    html = res.get_data(as_text=True)

    # Core sections
    assert "Discover the Right Course" in html
    assert "What is EduVerse AI?" in html
    assert "What We Offer" in html
    assert "How It Works" in html
    assert "AI-Based Course Recommendation" in html
    assert "Find Courses Your Way" in html
    assert "AI vs Normal Course Discovery" in html
    assert "Why EduVerse AI?" in html
    assert "Have a Question?" in html

    # Form fields
    assert 'name="student_name"' in html
    assert 'name="email"' in html
    assert 'name="phone"' in html
    assert 'name="category"' in html
    assert 'name="message"' in html
    assert "Submit Query" in html


def test_api_submit_student_query(client, app):
    """Verify that students can submit queries via REST API and they persist in the database."""
    payload = {
        'student_name': 'Karthik Raja',
        'email': 'karthik.raja@example.com',
        'phone': '9876543210',
        'category': 'AI Recommendation',
        'message': 'Can you explain how the 12th cutoff is evaluated for autonomous colleges?'
    }

    res = client.post('/api/queries', json=payload)
    assert res.status_code == 201
    data = res.get_json()
    assert data['success'] is True
    assert 'query' in data
    assert data['query']['status'] == 'PENDING'
    query_id = data['query']['id']

    # Verify persistent storage in SQLite DB
    with app.app_context():
        saved = StudentQuery.query.get(query_id)
        assert saved is not None
        assert saved.student_name == 'Karthik Raja'
        assert saved.email == 'karthik.raja@example.com'
        assert saved.category == 'AI Recommendation'
        assert saved.status == 'PENDING'
        assert saved.admin_response is None


def test_web_form_submit_student_query(client, app):
    """Verify standard web form submission with redirect and flash message."""
    form_data = {
        'student_name': 'Ananya Raman',
        'email': 'ananya.raman@example.com',
        'phone': '9123456780',
        'category': 'College Information',
        'message': 'Does Loyola College offer hostel facilities for MCA students?'
    }

    res = client.post('/about', data=form_data, follow_redirects=True)
    assert res.status_code == 200
    html = res.get_data(as_text=True)
    assert "submitted successfully" in html
    assert "Ananya Raman" in html

    with app.app_context():
        saved = StudentQuery.query.filter_by(email='ananya.raman@example.com').first()
        assert saved is not None
        assert saved.status == 'PENDING'


def test_admin_query_management_lifecycle(admin_client, app):
    """Verify admin can view, respond, change status, and delete queries."""
    with app.app_context():
        q = StudentQuery(
            student_name='Vignesh Kumar',
            email='vignesh.k@example.com',
            category='Course Information',
            message='I want to know which engineering branch has the highest placement in Coimbatore.',
            status='PENDING'
        )
        db.session.add(q)
        db.session.commit()
        qid = q.id

    # 1. Admin views queries list
    res_list = admin_client.get('/admin/queries')
    assert res_list.status_code == 200
    html_list = res_list.get_data(as_text=True)
    assert "Vignesh Kumar" in html_list
    assert "PENDING" in html_list

    # 2. Admin responds and marks RESOLVED
    res_resp = admin_client.post(f'/admin/queries/{qid}/respond', data={
        'admin_response': 'B.Tech AI & ML and CSE currently have 95%+ campus placements across Coimbatore autonomous colleges.',
        'status': 'RESOLVED'
    }, follow_redirects=True)
    assert res_resp.status_code == 200

    with app.app_context():
        updated = StudentQuery.query.get(qid)
        assert updated.status == 'RESOLVED'
        assert "95%+" in updated.admin_response

    # 3. Admin updates status directly to CLOSED
    res_status = admin_client.post(f'/admin/queries/{qid}/status', data={'status': 'CLOSED'}, follow_redirects=True)
    assert res_status.status_code == 200
    with app.app_context():
        assert StudentQuery.query.get(qid).status == 'CLOSED'

    # 4. Admin deletes query
    res_del = admin_client.post(f'/admin/queries/{qid}/delete', follow_redirects=True)
    assert res_del.status_code == 200
    with app.app_context():
        assert StudentQuery.query.get(qid) is None


def test_admin_dashboard_shows_query_metrics(admin_client, app):
    """Verify Admin Dashboard renders the Student Queries KPI card with pending count."""
    with app.app_context():
        q = StudentQuery(
            student_name='Divya S',
            email='divya.s@example.com',
            category='Feedback',
            message='The map navigation feature is extremely helpful for finding colleges.',
            status='PENDING'
        )
        db.session.add(q)
        db.session.commit()

    res = admin_client.get('/admin/')
    assert res.status_code == 200
    html = res.get_data(as_text=True)
    assert "Student Queries" in html
    assert "Recent Student Inquiries" in html
    assert "Divya S" in html


def test_unauthenticated_and_student_blocked_from_admin_queries(client, student_client):
    """Verify RBAC: unauthenticated and student users are blocked from admin queries."""
    # Unauthenticated
    assert client.get('/admin/queries').status_code == 403
    assert client.get('/api/admin/queries').status_code == 403

    # Student client
    assert student_client.get('/admin/queries').status_code == 403
    assert student_client.get('/api/admin/queries').status_code == 403


def test_ai_course_recommendation_api(client):
    """Verify AI course recommendation endpoint analyzes 12th marks and outputs matching courses."""
    payload = {
        'marks_12th': 88.0,
        'stream': 'Science (Maths)',
        'subject_marks': {
            'mathematics': 92,
            'computer_science': 95,
            'physics': 85
        },
        'interests': ['Software & AI']
    }

    res = client.post('/api/recommend/courses', json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert data['mode'] == 'AI_POWERED'
    assert len(data['courses']) > 0

    first = data['courses'][0]
    assert 'course_name' in first
    assert 'match_score' in first
    assert 'matching_factors' in first
    assert 'explore_url' in first
    assert first['match_score'] > 0


def test_normal_course_discovery_api(client):
    """Verify normal course discovery endpoint filters courses deterministically."""
    payload = {
        'marks_12th': 55.0,
        'stream': 'Commerce',
        'category': 'Commerce & Finance'
    }

    res = client.post('/api/courses/discover', json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert data['mode'] == 'NORMAL_DISCOVERY'
    assert len(data['courses']) > 0

    course_names = [c['course_name'] for c in data['courses']]
    assert 'B.Com' in course_names
