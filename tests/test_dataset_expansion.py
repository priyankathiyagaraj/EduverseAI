import pytest
from app import create_app, db
from app.models.college import College
from app.models.district import District
from app.models.course import Course
from app.models.facility import Facility
from app.models.dataset_metadata import DatasetMetadata
from app.services.college_service import CollegeService
from app.services.analytics_service import AnalyticsService
from app.services.recommendation_service import RecommendationService


def test_production_dataset_targets():
    """
    Validates that the active dataset meets all user-specified targets:
    - 500+ total unique institutions (PDF 1000 + district colleges)
    - All 38 Tamil Nadu districts covered with college records
    - Government >= 101
    - Government-Aided >= 101
    - Self-Financing >= 101
    - Autonomous >= 101
    """
    app = create_app('development')
    with app.app_context():
        total_colleges = College.query.count()
        assert total_colleges >= 501, f"Expected >= 501 colleges, found {total_colleges}"

        # District coverage
        districts = District.query.all()
        assert len(districts) == 38, f"Expected 38 districts, found {len(districts)}"
        districts_with_colleges = db.session.query(College.district).distinct().count()
        assert districts_with_colleges == 38, f"Expected all 38 districts to have colleges, found {districts_with_colleges}"

        # Category thresholds
        gov_count = College.query.filter(College.primary_college_type == 'GOVERNMENT').count()
        aided_count = College.query.filter(College.primary_college_type == 'GOVERNMENT_AIDED').count()
        sf_count = College.query.filter(College.primary_college_type == 'SELF_FINANCING').count()
        auto_count = College.query.filter(College.autonomous_status == 'AUTONOMOUS').count()

        assert gov_count >= 101, f"Expected >= 101 Government colleges, found {gov_count}"
        assert aided_count >= 101, f"Expected >= 101 Government-Aided colleges, found {aided_count}"
        assert sf_count >= 101, f"Expected >= 101 Self-Financing colleges, found {sf_count}"
        assert auto_count >= 101, f"Expected >= 101 Autonomous colleges, found {auto_count}"


def test_api_college_types_endpoint():
    """Tests that the new /api/college-types endpoint returns both primary types and autonomous statuses."""
    app = create_app('development')
    client = app.test_client()
    res = client.get('/api/college-types')
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert 'GOVERNMENT' in data['primary_types']
    assert 'GOVERNMENT_AIDED' in data['primary_types']
    assert 'SELF_FINANCING' in data['primary_types']
    assert 'AUTONOMOUS' in data['autonomous_statuses']
    assert 'NON_AUTONOMOUS' in data['autonomous_statuses']


def test_api_autonomous_filter():
    """Tests filtering /api/colleges by autonomous=AUTONOMOUS and autonomous=NON_AUTONOMOUS."""
    app = create_app('development')
    client = app.test_client()

    # Filter autonomous
    res_auto = client.get('/api/colleges?autonomous=AUTONOMOUS&per_page=20')
    assert res_auto.status_code == 200
    data_auto = res_auto.get_json()
    assert data_auto['success'] is True
    assert data_auto['pagination']['total'] >= 101
    for col in data_auto['colleges']:
        assert col['autonomous_status'] == 'AUTONOMOUS' or col['is_autonomous'] is True

    # Filter non-autonomous
    res_non_auto = client.get('/api/colleges?autonomous=NON_AUTONOMOUS&per_page=20')
    assert res_non_auto.status_code == 200
    data_non_auto = res_non_auto.get_json()
    assert data_non_auto['success'] is True
    assert data_non_auto['pagination']['total'] >= 101
    for col in data_non_auto['colleges']:
        assert col['autonomous_status'] != 'AUTONOMOUS'


def test_api_ownership_filter():
    """Tests filtering /api/colleges by college_type=Government."""
    app = create_app('development')
    client = app.test_client()

    res = client.get('/api/colleges?college_type=Government&per_page=20')
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert data['pagination']['total'] >= 101
    for col in data['colleges']:
        assert col['primary_college_type'] == 'GOVERNMENT' or 'Government' in col['college_type']


def test_analytics_metrics_comprehensive():
    """Tests that AnalyticsService returns 2D distribution metrics accurately."""
    app = create_app('development')
    with app.app_context():
        metrics = AnalyticsService.get_analytics_metrics()
        summary = metrics['summary']
        assert summary['total_colleges'] >= 501
        assert summary['government_count'] >= 101
        assert summary['aided_count'] >= 101
        assert summary['self_financing_count'] >= 101
        assert summary['autonomous_count'] >= 101

        # Check distribution structures
        assert 'labels' in metrics['ownership_distribution']
        assert 'counts' in metrics['ownership_distribution']
        assert 'labels' in metrics['autonomous_distribution']
        assert 'counts' in metrics['autonomous_distribution']
        assert 'labels' in metrics['colleges_by_city']
        assert 'counts' in metrics['colleges_by_city']


def test_recommendation_with_autonomy_preference():
    """Tests recommendation service scoring when autonomy preference is provided."""
    app = create_app('development')
    with app.app_context():
        # Request autonomous MCA colleges
        result = RecommendationService.get_recommendations({
            'course': 'MCA',
            'autonomous': 'AUTONOMOUS',
            'budget': 150000
        }, top_k=5)

        assert 'recommendations' in result
        assert len(result['recommendations']) > 0
        top = result['recommendations'][0]
        assert 'autonomous_status' in top
        assert 'is_autonomous' in top
        assert 'score' in top
        assert top['score'] > 0


def test_dataset_metadata_integrity():
    """Tests that DatasetMetadata table records active dataset provenance and versioning."""
    app = create_app('development')
    with app.app_context():
        meta = DatasetMetadata.query.order_by(DatasetMetadata.id.desc()).first()
        assert meta is not None, "Dataset metadata record should exist"
        assert meta.total_records >= 501
        assert meta.verified_records >= 501
        assert meta.dataset_version is not None
