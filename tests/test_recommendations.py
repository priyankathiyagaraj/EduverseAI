def test_recommendation_valid_input_and_structure(client):
    """Tests POST /api/recommend with full preference vector."""
    payload = {
        'course': 'MCA',
        'state': 'Tamil Nadu',
        'district': 'Chennai',
        'city': 'Chennai',
        'budget': 100000,
        'college_type': 'University Department',
        'facilities': ['Hostel', 'Central Library', 'Placement Cell']
    }
    res = client.post('/api/recommend', json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert 'recommendations' in data
    assert len(data['recommendations']) > 0
    assert 'disclaimer' in data

    # Verify structure of top recommendation
    top = data['recommendations'][0]
    assert 'college_id' in top
    assert 'college_name' in top
    assert 'score' in top
    assert 0.0 <= top['score'] <= 100.0
    assert 'matching_factors' in top
    assert len(top['matching_factors']) > 0
    assert 'location' in top
    assert 'data_status' in top


def test_recommendation_ranking_order(client):
    """Verifies that recommendation results are ordered in strictly descending score."""
    payload = {
        'course': 'MCA',
        'district': 'Coimbatore',
        'budget': 80000
    }
    res = client.post('/api/recommend', json=payload)
    assert res.status_code == 200
    recs = res.get_json()['recommendations']
    scores = [r['score'] for r in recs]
    assert scores == sorted(scores, reverse=True)


def test_recommendation_invalid_budget(client):
    """Tests that negative budget is rejected with validation error."""
    payload = {
        'course': 'MCA',
        'budget': -10000
    }
    res = client.post('/api/recommend', json=payload)
    assert res.status_code == 400
    data = res.get_json()
    assert data['success'] is False
    assert data['error']['code'] == 'VALIDATION_ERROR'


def test_recommendation_no_matching_course(client):
    """Tests recommendation behavior when requesting a program not cataloged."""
    payload = {
        'course': 'NonExistentDegreeProgramXYZ',
        'budget': 50000
    }
    res = client.post('/api/recommend', json=payload)
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert len(data['recommendations']) == 0


def test_recommendation_empty_preferences_handled(client):
    """Tests that an empty preference dictionary does not crash and returns default ranked set."""
    res = client.post('/api/recommend', json={})
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert len(data['recommendations']) > 0
