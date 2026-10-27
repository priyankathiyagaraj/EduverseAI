import pytest
from app import db
from app.models.user import User
from app.models.student_query import StudentQuery
from app.models.student_profile import StudentProfile
from app.models.college import College


def test_homepage_metrics_pre_rendered(client):
    """Verify that homepage renders database metrics server-side instead of dashes."""
    response = client.get('/')
    assert response.status_code == 200
    html = response.data.decode('utf-8')
    # Should not contain raw dashes inside the stat numbers
    assert '<div id="stat-colleges" class="text-2xl sm:text-3xl font-extrabold text-slate-900">—</div>' not in html
    assert '<div id="stat-courses" class="text-2xl sm:text-3xl font-extrabold text-blue-600">—</div>' not in html
    assert '<div id="stat-districts" class="text-2xl sm:text-3xl font-extrabold text-slate-900">—</div>' not in html
    assert 'Colleges Indexed' in html
    assert 'Courses Cataloged' in html
    assert 'Districts Covered' in html


def test_footer_database_technology_label(client):
    """Verify footer displays dynamic database backend rather than hardcoded MySQL."""
    response = client.get('/')
    assert response.status_code == 200
    html = response.data.decode('utf-8')
    assert 'SQLAlchemy' in html
    # In SQLite test environment, it should mention SQLite or PostgreSQL in prod
    assert 'SQLite & SQLAlchemy' in html or 'PostgreSQL & SQLAlchemy' in html


def test_student_registration_login_logout(client):
    """Test full authentication flow: register new student, login, and logout."""
    # 1. Registration
    reg_payload = {
        'name': 'Test Student Registration',
        'email': 'unique_student_test@example.com',
        'password': 'SecurePassword123!',
        'confirm_password': 'SecurePassword123!'
    }
    reg_resp = client.post('/register', data=reg_payload, follow_redirects=True)
    assert reg_resp.status_code == 200
    assert 'Welcome to EduVerse AI' in reg_resp.data.decode('utf-8') or 'Explore' in reg_resp.data.decode('utf-8')

    # Verify session is established
    with client.session_transaction() as sess:
        assert 'user' in sess
        assert sess['user']['email'] == 'unique_student_test@example.com'
        assert sess['user']['role'] == 'student'

    # 2. Logout
    logout_resp = client.get('/logout', follow_redirects=True)
    assert logout_resp.status_code == 200
    with client.session_transaction() as sess:
        assert 'user' not in sess

    # 3. Login
    login_payload = {
        'email': 'unique_student_test@example.com',
        'password': 'SecurePassword123!'
    }
    login_resp = client.post('/login', data=login_payload, follow_redirects=True)
    assert login_resp.status_code == 200
    with client.session_transaction() as sess:
        assert 'user' in sess
        assert sess['user']['email'] == 'unique_student_test@example.com'


def test_college_exploration_and_api(client):
    """Test college exploration page and search API."""
    explore_resp = client.get('/explore')
    assert explore_resp.status_code == 200
    assert 'Explore' in explore_resp.data.decode('utf-8')

    api_resp = client.get('/api/colleges?per_page=5')
    assert api_resp.status_code == 200
    data = api_resp.get_json()
    assert data['success'] is True
    assert 'colleges' in data
    assert len(data['colleges']) > 0


def test_recommendations_page_and_api(client):
    """Test recommendation interface and recommendation algorithm API."""
    rec_page_resp = client.get('/recommendations')
    assert rec_page_resp.status_code == 200

    payload = {
        'course': 'MCA',
        'district': 'Chennai',
        'budget': 100000,
        'facilities': []
    }
    api_rec_resp = client.post('/api/recommend', json=payload)
    assert api_rec_resp.status_code == 200
    data = api_rec_resp.get_json()
    assert data['success'] is True
    assert 'recommendations' in data


def test_comparison_page_and_api(client):
    """Test comparison matrix and adding colleges."""
    compare_page = client.get('/compare')
    assert compare_page.status_code == 200

    colleges_resp = client.get('/api/colleges?per_page=1')
    first_id = colleges_resp.get_json()['colleges'][0]['id']

    add_resp = client.post('/api/compare', json={'college_id': first_id})
    assert add_resp.status_code == 200
    data = add_resp.get_json()
    assert data['success'] is True
    assert data['compare_count'] >= 1


def test_map_page(client):
    """Test the college map page."""
    map_resp = client.get('/map')
    assert map_resp.status_code == 200
    assert 'Leaflet' in map_resp.data.decode('utf-8') or 'map' in map_resp.data.decode('utf-8').lower()


def test_feedback_submission(client):
    """Test feedback submission via API."""
    fb_payload = {
        'student_name': 'Feedback Tester',
        'email': 'tester@example.com',
        'rating': 5,
        'category': 'General',
        'feedback_message': 'EduVerse AI is intuitive and accurate.'
    }
    fb_resp = client.post('/api/feedback', json=fb_payload)
    assert fb_resp.status_code == 201
    data = fb_resp.get_json()
    assert data['success'] is True


def test_unauthenticated_and_student_blocked_from_admin(client, student_client):
    """Test that unauthenticated users and students are strictly blocked with HTTP 403."""
    # Unauthenticated client
    unauth_admin = client.get('/admin')
    assert unauth_admin.status_code == 403

    unauth_api = client.get('/api/admin/feedback')
    assert unauth_api.status_code == 403

    # Student client (should be blocked with 403)
    student_admin = student_client.get('/admin')
    assert student_admin.status_code == 403

    student_api = student_client.get('/api/admin/feedback')
    assert student_api.status_code == 403


def test_admin_access_granted(admin_client):
    """Test that authenticated administrator is granted access."""
    admin_page = admin_client.get('/admin')
    assert admin_page.status_code == 200

    admin_api = admin_client.get('/api/admin/feedback')
    assert admin_api.status_code == 200


def test_student_privacy_isolation(app, client):
    """
    Test student privacy isolation:
    Confirm students cannot access other students' private queries or records.
    """
    with app.app_context():
        # Create student A
        student_a = User(name='Student Alice', email='alice@student.test', role='student')
        student_a.set_password('Pass1234!')
        db.session.add(student_a)

        # Create student B
        student_b = User(name='Student Bob', email='bob@student.test', role='student')
        student_b.set_password('Pass1234!')
        db.session.add(student_b)
        db.session.commit()

        # Alice's private query
        q_alice = StudentQuery(
            student_id=student_a.id,
            student_name=student_a.name,
            email=student_a.email,
            category='Counseling',
            message='Alice private inquiry about MCA cutoff',
            status='PENDING'
        )
        # Bob's private query
        q_bob = StudentQuery(
            student_id=student_b.id,
            student_name=student_b.name,
            email=student_b.email,
            category='Admission',
            message='Bob private inquiry about hostel fee',
            status='PENDING'
        )
        db.session.add_all([q_alice, q_bob])
        db.session.commit()

        alice_dict = student_a.to_dict()
        bob_dict = student_b.to_dict()

    # Log in as Alice
    with client.session_transaction() as sess:
        sess['user'] = alice_dict

    alice_queries_resp = client.get('/api/student/queries')
    assert alice_queries_resp.status_code == 200
    alice_data = alice_queries_resp.get_json()
    assert alice_data['success'] is True
    # Alice must only see her own queries, never Bob's
    query_messages = [q['message'] for q in alice_data['queries']]
    assert any('Alice private inquiry' in m for m in query_messages)
    assert not any('Bob private inquiry' in m for m in query_messages)

    # Now log in as Bob
    with client.session_transaction() as sess:
        sess['user'] = bob_dict

    bob_queries_resp = client.get('/api/student/queries')
    assert bob_queries_resp.status_code == 200
    bob_data = bob_queries_resp.get_json()
    assert bob_data['success'] is True
    # Bob must only see his own queries, never Alice's
    bob_messages = [q['message'] for q in bob_data['queries']]
    assert any('Bob private inquiry' in m for m in bob_messages)
    assert not any('Alice private inquiry' in m for m in bob_messages)
