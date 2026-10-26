from app import db
from app.models import College, Course, Facility


def test_analytics_metrics_valid_dataset(client):
    """Tests GET /api/analytics returns accurate database aggregations."""
    res = client.get('/api/analytics')
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True

    # Check summary
    summary = data['summary']
    assert summary['total_colleges'] >= 15
    assert summary['total_courses'] >= 30
    assert summary['total_districts'] >= 10

    # Check charts
    assert len(data['colleges_by_district']['labels']) == len(data['colleges_by_district']['counts'])
    assert len(data['colleges_by_type']['labels']) == len(data['colleges_by_type']['counts'])
    assert len(data['fee_distribution']['labels']) == 6
    assert sum(data['fee_distribution']['counts']) == summary['total_courses']


def test_analytics_page_html_render(client):
    """Tests that the /analytics dashboard renders."""
    res = client.get('/analytics')
    assert res.status_code == 200
    assert b'Institutional Analytics &amp; Distributions' in res.data or b'Institutional Analytics' in res.data


def test_analytics_empty_database_handling(app):
    """Verifies that an empty database returns zeroed counts without raising errors."""
    with app.app_context():
        # Clear all colleges, courses, facilities
        Course.query.delete()
        Facility.query.delete()
        College.query.delete()
        db.session.commit()

        client = app.test_client()
        res = client.get('/api/analytics')
        assert res.status_code == 200
        data = res.get_json()
        assert data['success'] is True
        assert data['summary']['total_colleges'] == 0
        assert data['summary']['total_courses'] == 0
        assert len(data['colleges_by_district']['labels']) == 38
        assert all(count == 0 for count in data['colleges_by_district']['counts'])
