def test_add_to_comparison_and_retrieve(client):
    """Tests adding institutions to the comparison list and fetching matrix."""
    # Add College 1
    r1 = client.post('/api/compare', json={'college_id': 1})
    assert r1.status_code == 200
    assert r1.get_json()['compare_count'] == 1

    # Add College 2
    r2 = client.post('/api/compare', json={'college_id': 2})
    assert r2.status_code == 200
    assert r2.get_json()['compare_count'] == 2

    # Fetch comparison matrix
    res_get = client.get('/api/compare')
    assert res_get.status_code == 200
    data = res_get.get_json()
    assert data['success'] is True
    assert data['count'] == 2
    assert data['is_ready'] is True  # 2 colleges meet minimum requirement


def test_comparison_duplicate_prevention(client):
    """Tests that adding an already present college returns 400 error."""
    client.post('/api/compare', json={'college_id': 1})
    # Attempt duplicate
    res_dup = client.post('/api/compare', json={'college_id': 1})
    assert res_dup.status_code == 400
    data = res_dup.get_json()
    assert data['success'] is False
    assert data['error']['code'] == 'COMPARISON_LIMIT_OR_DUPLICATE'


def test_comparison_maximum_four_colleges(client):
    """Tests that attempting to add a 5th college is blocked."""
    # Add colleges 1, 2, 3, 4
    for cid in [1, 2, 3, 4]:
        r = client.post('/api/compare', json={'college_id': cid})
        assert r.status_code == 200

    # Attempt to add 5th college
    r5 = client.post('/api/compare', json={'college_id': 5})
    assert r5.status_code == 400
    data = r5.get_json()
    assert data['success'] is False
    assert 'at most 4' in data['error']['message']


def test_comparison_remove_and_clear(client):
    """Tests removing specific college and clearing all."""
    client.post('/api/compare', json={'college_id': 1})
    client.post('/api/compare', json={'college_id': 2})

    # Remove college 1
    res_rem = client.delete('/api/compare/1')
    assert res_rem.status_code == 200
    assert res_rem.get_json()['compare_count'] == 1

    # Clear matrix
    res_clear = client.post('/api/compare/clear')
    assert res_clear.status_code == 200
    assert res_clear.get_json()['compare_count'] == 0


def test_compare_html_page_render(client):
    """Tests that /compare renders successfully."""
    res = client.get('/compare')
    assert res.status_code == 200
    assert b'College Comparison Matrix' in res.data
