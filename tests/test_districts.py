import pytest
from app import db
from app.models.district import District
from app.models.college import College
from seed.seed_data import MANDATORY_TN_DISTRICTS


def test_all_38_districts_exist_in_database(app):
    """Verifies that all 38 Tamil Nadu districts are seeded in the database."""
    with app.app_context():
        districts = District.query.all()
        assert len(districts) == 38
        assert len(MANDATORY_TN_DISTRICTS) == 38


def test_no_duplicate_districts_in_database(app):
    """Verifies that every district name is unique with zero duplicates."""
    with app.app_context():
        districts = District.query.all()
        names = [d.name for d in districts]
        assert len(names) == len(set(names))
        assert set(names) == set(MANDATORY_TN_DISTRICTS)


def test_foreign_key_referential_integrity(app):
    """Verifies that every college has a valid district_id pointing to districts.id."""
    with app.app_context():
        colleges = College.query.all()
        assert len(colleges) > 0
        for col in colleges:
            assert col.district_id is not None
            district = db.session.get(District, col.district_id)
            assert district is not None
            assert district.name == col.district


def test_api_districts_returns_all_38(client):
    """Tests GET /api/districts returns all 38 districts and metadata."""
    res = client.get('/api/districts')
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert data['total_districts'] == 38
    assert len(data['districts']) == 38
    assert "Chennai" in data['districts']
    assert "Theni" in data['districts']
    assert "The Nilgiris" in data['districts']
    assert "Tiruvarur" in data['districts']


def test_explore_filter_district_with_colleges(client):
    """Tests filtering by a populated district returns its colleges."""
    res = client.get('/api/colleges?district=Chennai')
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert len(data['colleges']) > 0
    for col in data['colleges']:
        assert col['district'] == 'Chennai'


def test_kanyakumari_district_name_resolution(client):
    """Tests that 'Kanyakumari', 'Kanniyakumari', and 'Kanyakumari District' all resolve to colleges."""
    for variant in ['Kanyakumari', 'Kanniyakumari', 'Kanyakumari District']:
        res = client.get(f'/api/colleges?district={variant}')
        assert res.status_code == 200
        data = res.get_json()
        assert data['success'] is True
        assert len(data['colleges']) >= 2, f"Failed for variant: {variant}"
        for col in data['colleges']:
            assert col['district'] == 'Kanyakumari'


def test_seed_database_idempotency(app):
    """Verifies that calling seed_database() repeatedly does not create duplicate records."""
    from seed.seed_data import seed_database
    with app.app_context():
        initial_districts = District.query.count()
        initial_colleges = College.query.count()

        # Re-run seed
        seed_database()

        assert District.query.count() == initial_districts
        assert College.query.count() == initial_colleges


def test_explore_filter_district_without_colleges(client, app):
    """Tests filtering by an unpopulated district returns 0 colleges gracefully."""
    with app.app_context():
        empty_dist = District(name="Unpopulated Test District", state="Tamil Nadu")
        db.session.add(empty_dist)
        db.session.commit()

    res = client.get('/api/colleges?district=Unpopulated%20Test%20District')
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert len(data['colleges']) == 0
    assert data['pagination']['total'] == 0


def test_recommendation_district_without_colleges_returns_transparent_message(client, app):
    """Tests that recommender returns the exact required message for an unpopulated district."""
    with app.app_context():
        empty_dist = District(name="Empty Test District", state="Tamil Nadu")
        db.session.add(empty_dist)
        db.session.commit()

    payload = {
        "course": "MCA",
        "state": "Tamil Nadu",
        "district": "Empty Test District",
        "budget": 100000
    }
    res = client.post('/api/recommend', json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert data['recommendations'] == []
    assert data['message'] == "No college information is currently available for the selected district."


def test_analytics_district_chart_covers_all_38(client):
    """Tests that analytics endpoint calculates statistics across all 38 districts."""
    res = client.get('/api/analytics')
    assert res.status_code == 200
    data = res.get_json()
    district_data = data['colleges_by_district']
    assert len(district_data['labels']) >= 38
    assert len(district_data['counts']) >= 38
    assert "Theni" in district_data['labels']
    assert "Chennai" in district_data['labels']
    assert "Kanyakumari" in district_data['labels']
    assert district_data['total_districts_supported'] == 38
    assert district_data['districts_with_colleges'] == 38
    assert district_data['districts_without_colleges'] == 0

