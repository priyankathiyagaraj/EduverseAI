def test_unauthenticated_and_student_blocked_from_admin(client, student_client):
    """Verifies server-side authorization: unauthenticated and student users cannot access admin."""
    # 1. Unauthenticated
    res_unauth = client.get('/admin')
    assert res_unauth.status_code == 403

    # 2. Student client
    res_student = student_client.get('/admin')
    assert res_student.status_code == 403

    # 3. Student attempting admin API
    res_api = student_client.post('/api/admin/colleges', json={'name': 'Hacked College'})
    assert res_api.status_code == 403


def test_admin_dashboard_access_allowed(admin_client):
    """Verifies that authenticated admin can access admin dashboard."""
    res = admin_client.get('/admin')
    assert res.status_code == 200
    assert b'Admin Dashboard' in res.data


def test_admin_college_crud_lifecycle(admin_client):
    """Tests complete Admin CRUD lifecycle: create, update, and delete."""
    # 1. Create College
    payload = {
        'name': 'Government College of Engineering, Bodinayakkanur',
        'code': 'GCE-BODI',
        'state': 'Tamil Nadu',
        'district': 'Theni',
        'city': 'Bodinayakkanur',
        'college_type': 'Government',
        'latitude': 10.0104,
        'longitude': 77.3498,
        'data_status': 'VERIFIED',
        'courses': [
            {'name': 'MCA', 'fee': 22000.0, 'duration': 2.0},
            {'name': 'B.E. Computer Science', 'fee': 18000.0, 'duration': 4.0}
        ],
        'facilities': ['Hostel', 'Central Library', 'Laboratories']
    }
    res_create = admin_client.post('/api/admin/colleges', json=payload)
    assert res_create.status_code == 201
    created_col = res_create.get_json()['college']
    col_id = created_col['id']
    assert created_col['name'] == 'Government College of Engineering, Bodinayakkanur'
    assert len(created_col['courses']) == 2
    assert len(created_col['facilities']) == 3

    # 2. Update College
    res_update = admin_client.put(f'/api/admin/colleges/{col_id}', json={
        'name': 'Government College of Engineering, Theni (Bodi Campus)',
        'website': 'https://gcebodi.ac.in'
    })
    assert res_update.status_code == 200
    updated_col = res_update.get_json()['college']
    assert updated_col['name'] == 'Government College of Engineering, Theni (Bodi Campus)'
    assert updated_col['website'] == 'https://gcebodi.ac.in'

    # 3. Delete College
    res_delete = admin_client.delete(f'/api/admin/colleges/{col_id}')
    assert res_delete.status_code == 200
    assert res_delete.get_json()['success'] is True

    # 4. Verify college is deleted (returns 404)
    res_check = admin_client.get(f'/api/colleges/{col_id}')
    assert res_check.status_code == 404
