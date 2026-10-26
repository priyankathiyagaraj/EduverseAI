from app.models.college import College
from app.models.course import Course
from app.services.college_service import CollegeService


def test_discovery_combination_filter(client):
    """
    Tests the core project concept:
    DISTRICT -> COURSE -> INSTITUTION TYPE -> COLLEGE DISCOVERY
    """
    res = client.get('/api/colleges?district=Chennai&course=MCA&college_type=Autonomous')
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert 'colleges' in data
    assert 'pagination' in data
    # In test DB (which has Anna University / CEG in Chennai), verify results match filters
    if data['colleges']:
        for col in data['colleges']:
            assert col['district'] == 'Chennai'
            assert col['is_autonomous'] or 'autonomous' in col['college_type'].lower()
            course_names = [crs['course_name'] for crs in col['courses']]
            assert any('MCA' in c for c in course_names)


def test_college_fields_and_directions_url(client):
    """
    Tests that all college records have valid coordinates, google_maps_url,
    directions_url, accreditation, affiliation, and ratings.
    """
    res = client.get('/api/colleges?per_page=10')
    assert res.status_code == 200
    data = res.get_json()
    for col in data['colleges']:
        assert col['latitude'] is not None
        assert col['longitude'] is not None
        assert col['has_coordinates'] is True
        assert 'google_maps_url' in col and col['google_maps_url']
        assert 'directions_url' in col and col['directions_url']
        assert 'https://www.google.com/maps' in col['directions_url']
        assert 'rating' in col and col['rating'] is not None


def test_course_extended_fields(client):
    """
    Tests that courses have degree, department, intake_seats, and admission_mode.
    """
    res = client.get('/api/colleges?per_page=10')
    assert res.status_code == 200
    data = res.get_json()
    all_courses = []
    for col in data['colleges']:
        all_courses.extend(col.get('courses', []))

    assert len(all_courses) > 0
    for crs in all_courses:
        assert 'degree' in crs
        assert 'department' in crs
        assert 'intake_seats' in crs
        assert 'admission_mode' in crs


def test_map_page_render_and_accessibility(client):
    """
    Tests that the campus map view loads with 200 and contains OpenStreetMap integration.
    """
    res = client.get('/map')
    assert res.status_code == 200
    assert b'Tamil Nadu Institutional Map' in res.data
    assert b'tn-leaflet-map' in res.data
