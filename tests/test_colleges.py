from app.models.college import College


def test_explore_page_render(client):
    """Tests that the Explorer UI page loads with status 200."""
    res = client.get('/explore')
    assert res.status_code == 200
    assert b'College Explorer' in res.data


def test_api_colleges_list_and_pagination(client):
    """Tests GET /api/colleges returns paginated response."""
    res = client.get('/api/colleges?page=1&per_page=5')
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert len(data['colleges']) <= 5
    assert 'pagination' in data
    assert data['pagination']['total'] >= 15


def test_search_by_college_name(client):
    """Tests searching for an institution by keyword."""
    res = client.get('/api/colleges?query=Guindy')
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert len(data['colleges']) >= 1
    assert 'Guindy' in data['colleges'][0]['name']


def test_filter_by_course(client):
    """Tests filtering institutions offering a specific program (e.g. MCA)."""
    res = client.get('/api/colleges?course=MCA')
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert len(data['colleges']) > 0
    for col in data['colleges']:
        course_names = [crs['course_name'] for crs in col['courses']]
        assert any('MCA' in c for c in course_names)


def test_filter_by_district(client):
    """Tests filtering colleges by district."""
    res = client.get('/api/colleges?district=Coimbatore')
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert len(data['colleges']) >= 2
    for col in data['colleges']:
        assert col['district'] == 'Coimbatore'


def test_filter_by_max_fee(client):
    """Tests filtering colleges by maximum annual tuition fee limit."""
    res = client.get('/api/colleges?max_fee=25000')
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert len(data['colleges']) > 0
    for col in data['colleges']:
        # College must have at least one course with annual_fee <= 25000
        eligible_fees = [crs['annual_fee'] for crs in col['courses'] if crs['annual_fee'] is not None]
        assert any(f <= 25000 for f in eligible_fees)


def test_college_detail_valid_and_invalid_id(client, app):
    """Tests retrieving college details by ID, and checks 404 for non-existent IDs."""
    with app.app_context():
        from app import db
        first_college = db.session.get(College, 1)
        college_name = first_college.name.encode('utf-8')

    res_valid = client.get('/college/1')
    assert res_valid.status_code == 200
    assert college_name in res_valid.data

    res_api_valid = client.get('/api/colleges/1')
    assert res_api_valid.status_code == 200
    data = res_api_valid.get_json()
    assert data['success'] is True
    assert data['college']['id'] == 1
    assert len(data['college']['courses']) > 0
    assert len(data['college']['facilities']) > 0

    # Invalid ID 99999
    res_invalid = client.get('/college/99999')
    assert res_invalid.status_code == 404

    res_api_invalid = client.get('/api/colleges/99999')
    assert res_api_invalid.status_code == 404
    assert res_api_invalid.get_json()['success'] is False


def test_courses_and_districts_metadata_apis(client):
    """Tests auxiliary metadata API endpoints."""
    res_courses = client.get('/api/courses')
    assert res_courses.status_code == 200
    courses_data = res_courses.get_json()
    assert 'MCA' in courses_data['courses']

    res_districts = client.get('/api/districts')
    assert res_districts.status_code == 200
    districts_data = res_districts.get_json()
    assert 'Chennai' in districts_data['districts']
    assert 'Coimbatore' in districts_data['districts']
