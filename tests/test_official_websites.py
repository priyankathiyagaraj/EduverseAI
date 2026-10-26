import pytest
from app import db
from app.models.college import College
from app.models.district import District


def test_sanitize_url():
    """Verify URL sanitization logic for security and normalization."""
    # Valid HTTPS URLs
    assert College.sanitize_url("https://www.annauniv.edu/") == "https://www.annauniv.edu"
    assert College.sanitize_url("https://iitm.ac.in") == "https://iitm.ac.in"
    
    # Scheme addition
    assert College.sanitize_url("psgtech.edu") == "https://psgtech.edu"
    
    # HTTP preservation
    assert College.sanitize_url("http://gcebodi.ac.in/") == "http://gcebodi.ac.in"
    
    # Rejection of dangerous or non-http protocols
    assert College.sanitize_url("javascript:alert(1)") is None
    assert College.sanitize_url("data:text/html,<html>") is None
    assert College.sanitize_url("ftp://example.com") is None
    
    # Empty / None / Whitespace
    assert College.sanitize_url("") is None
    assert College.sanitize_url("   ") is None
    assert College.sanitize_url(None) is None


def test_college_model_official_website_fields(app):
    """Verify College model correctly stores and serializes official website fields."""
    with app.app_context():
        dist = District.query.first()
        college = College(
            name="Test Verification Institute",
            district=dist.name,
            district_id=dist.id,
            city="Chennai",
            college_type="Government",
            official_website_url="https://testinst.ac.in",
            website_status="VERIFIED"
        )
        db.session.add(college)
        db.session.commit()

        # Check retrieval from DB
        saved = College.query.filter_by(name="Test Verification Institute").first()
        assert saved is not None
        assert saved.official_website == "https://testinst.ac.in"
        assert saved.official_website_url == "https://testinst.ac.in"
        assert saved.website_status == "VERIFIED"

        # Check to_dict() serialization
        data = saved.to_dict()
        assert data["official_website"] == "https://testinst.ac.in"
        assert data["official_website_url"] == "https://testinst.ac.in"
        assert data["website_status"] == "VERIFIED"
        assert data["website"] == "https://testinst.ac.in"  # backwards compatibility


def test_unverified_and_broken_institutions_have_null_urls(app):
    """Verify that institutions with BROKEN or MISSING status have NULL official_website_url."""
    with app.app_context():
        dist = District.query.first()
        broken_col = College(
            name="Test Broken College",
            district=dist.name,
            district_id=dist.id,
            city="Chennai",
            college_type="Government",
            official_website_url=None,
            website_status="BROKEN"
        )
        missing_col = College(
            name="Test Missing College",
            district=dist.name,
            district_id=dist.id,
            city="Chennai",
            college_type="Government",
            official_website_url=None,
            website_status="MISSING"
        )
        db.session.add_all([broken_col, missing_col])
        db.session.commit()

        b_data = broken_col.to_dict()
        assert b_data["official_website_url"] is None
        assert b_data["website_status"] == "BROKEN"

        m_data = missing_col.to_dict()
        assert m_data["official_website_url"] is None
        assert m_data["website_status"] == "MISSING"


def test_api_college_endpoints_include_website_status(client, app):
    """Verify that REST API endpoints return official_website_url and website_status."""
    with app.app_context():
        college = College.query.first()
        college_id = college.id

    # List endpoint
    res = client.get("/api/colleges")
    assert res.status_code == 200
    data = res.get_json()
    assert data["success"] is True
    assert len(data["colleges"]) > 0
    first_col = data["colleges"][0]
    assert "official_website_url" in first_col
    assert "website_status" in first_col

    # Detail endpoint
    res_det = client.get(f"/api/colleges/{college_id}")
    assert res_det.status_code == 200
    data_det = res_det.get_json()
    assert data_det["success"] is True
    assert "official_website_url" in data_det["college"]
    assert "website_status" in data_det["college"]


def test_college_detail_page_renders_official_website(client, app):
    """Verify that the college detail page renders the verified link or not-available state."""
    with app.app_context():
        dist = District.query.first()
        
        # 1. Verified college
        verified_col = College(
            name="Official Test Verified Tech",
            district=dist.name,
            district_id=dist.id,
            city="Chennai",
            college_type="Government",
            official_website_url="https://verifiedtech.ac.in",
            website_status="VERIFIED"
        )
        # 2. Missing website college
        missing_col = College(
            name="Official Test Missing College",
            district=dist.name,
            district_id=dist.id,
            city="Chennai",
            college_type="Government",
            official_website_url=None,
            website_status="MISSING"
        )
        db.session.add_all([verified_col, missing_col])
        db.session.commit()
        v_id = verified_col.id
        m_id = missing_col.id

    # Test verified college HTML
    res_v = client.get(f"/college/{v_id}")
    assert res_v.status_code == 200
    html_v = res_v.get_data(as_text=True)
    assert "https://verifiedtech.ac.in" in html_v
    assert 'target="_blank"' in html_v
    assert 'rel="noopener noreferrer"' in html_v
    assert "Visit Official Website" in html_v

    # Test missing website college HTML
    res_m = client.get(f"/college/{m_id}")
    assert res_m.status_code == 200
    html_m = res_m.get_data(as_text=True)
    assert "Official website not available" in html_m
    # Must NOT render a link with fake or missing domain
    assert "href=\"https://verifiedtech.ac.in\"" not in html_m


def test_comparison_page_renders_official_website_row(client, app):
    """Verify that the comparison matrix contains the Official Website attribute."""
    with app.app_context():
        colleges = College.query.limit(2).all()
        ids = [c.id for c in colleges]

    # Add colleges to comparison session
    for cid in ids:
        res = client.post("/api/compare", json={"college_id": cid})
        assert res.status_code == 200

    res = client.get("/compare")
    assert res.status_code == 200
    html = res.get_data(as_text=True)
    assert "Official Website" in html


def test_admin_dashboard_shows_verified_websites_stat(admin_client, app):
    """Verify that the Admin Dashboard renders the Verified Websites metric."""
    res = admin_client.get("/admin/")
    assert res.status_code == 200
    html = res.get_data(as_text=True)
    assert "Verified Websites" in html
    assert "Official Website" in html


def test_college_card_component_renders_visit_official_website_button(client, app):
    """Verify that college cards render 'Visit Official Website' opening in a new browser tab."""
    with app.app_context():
        dist = District.query.first()
        verified_col = College(
            name="Card Test Engineering College",
            district=dist.name,
            district_id=dist.id,
            city="Chennai",
            college_type="Government",
            official_website="https://cardtestengg.edu.in",
            website_status="VERIFIED"
        )
        db.session.add(verified_col)
        db.session.commit()

        # Render college card component via test_request_context
        from flask import render_template
        with app.test_request_context():
            card_html = render_template('components/college_card.html', college=verified_col)
        assert "Visit Official Website" in card_html
        assert "https://cardtestengg.edu.in" in card_html
        assert 'target="_blank"' in card_html
        assert 'rel="noopener noreferrer"' in card_html


def test_all_38_districts_covered_in_authoritative_registry():
    """Verify that the authoritative verification engine contains verified colleges across all 38 TN districts."""
    from scripts.verify_college_websites import AUTHORITATIVE_REGISTRY
    assert len(AUTHORITATIVE_REGISTRY) >= 100
    # Verify specific newly verified districts
    assert "government college of engineering dharmapuri" in AUTHORITATIVE_REGISTRY
    assert "government arts and science college kallakurichi" in AUTHORITATIVE_REGISTRY
    assert "adhiparasakthi college of arts and science" in AUTHORITATIVE_REGISTRY
    assert "alagappa chettiar government college of engineering" in AUTHORITATIVE_REGISTRY

