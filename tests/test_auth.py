from app.models.user import User


def test_user_password_hashing(app):
    """Verifies that plaintext passwords are never stored and password verification works."""
    with app.app_context():
        user = User(name='Security Test', email='sec@eduverse.ac.in', role='student')
        user.set_password('MyStrongPassword!2026')
        assert user.password_hash != 'MyStrongPassword!2026'
        assert user.check_password('MyStrongPassword!2026') is True
        assert user.check_password('WrongPassword') is False


def test_student_registration_success(client):
    """Tests successful registration via API."""
    res = client.post('/api/auth/register', json={
        'name': 'Praveen Kumar',
        'email': 'praveen@test.com',
        'password': 'Password123'
    })
    assert res.status_code == 201
    data = res.get_json()
    assert data['success'] is True
    assert data['user']['email'] == 'praveen@test.com'
    assert data['user']['role'] == 'student'


def test_registration_duplicate_email(client):
    """Tests duplicate email rejection (HTTP 409)."""
    # Attempt to register with the seeded student email
    res = client.post('/api/auth/register', json={
        'name': 'Duplicate User',
        'email': 'student@eduverse.ac.in',
        'password': 'Password123'
    })
    assert res.status_code == 409
    data = res.get_json()
    assert data['success'] is False
    assert data['error']['code'] == 'DUPLICATE_EMAIL'


def test_registration_validation_errors(client):
    """Tests input validation failures on registration."""
    # Empty name
    res = client.post('/api/auth/register', json={
        'name': '',
        'email': 'valid@test.com',
        'password': 'Password123'
    })
    assert res.status_code == 400

    # Invalid email
    res = client.post('/api/auth/register', json={
        'name': 'Valid Name',
        'email': 'not-an-email',
        'password': 'Password123'
    })
    assert res.status_code == 400

    # Short password
    res = client.post('/api/auth/register', json={
        'name': 'Valid Name',
        'email': 'valid@test.com',
        'password': '123'
    })
    assert res.status_code == 400


def test_user_login_success_and_logout(client):
    """Tests login with seeded student credentials and subsequent logout."""
    res = client.post('/api/auth/login', json={
        'email': 'student@eduverse.ac.in',
        'password': 'Student@123'
    })
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert data['user']['email'] == 'student@eduverse.ac.in'

    # Logout
    res_logout = client.post('/api/auth/logout')
    assert res_logout.status_code == 200


def test_user_login_invalid_credentials(client):
    """Tests login failure with wrong password."""
    res = client.post('/api/auth/login', json={
        'email': 'student@eduverse.ac.in',
        'password': 'WrongPassword999'
    })
    assert res.status_code == 401
    data = res.get_json()
    assert data['success'] is False
    assert data['error']['code'] == 'INVALID_CREDENTIALS'
