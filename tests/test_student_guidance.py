import pytest
import json
from app import db
from app.models.user import User
from app.models.student_profile import StudentProfile
from app.models.student_query import StudentQuery
from app.services.assessment_service import AssessmentService
from app.services.ai_counselor_service import AICounselorService


def test_tnea_cutoff_calculation():
    """
    Verifies the TNEA cutoff calculation:
    TNEA cutoff = Mathematics mark / 2 + Physics mark / 4 + Chemistry mark / 4
    and standard 200 scale = Maths + Physics/2 + Chemistry/2
    """
    cutoff_res = AssessmentService.calculate_tnea_cutoff(90.0, 80.0, 80.0)
    # 90/2 = 45; 80/4 = 20; 80/4 = 20 => 45 + 20 + 20 = 85.0
    assert cutoff_res['formula_cutoff'] == 85.0
    # 90 + 40 + 40 = 170.0
    assert cutoff_res['standard_200_cutoff'] == 170.0
    assert 'breakdown' in cutoff_res
    assert 'disclaimer' in cutoff_res
    assert 'tneaonline.org' in cutoff_res['disclaimer']


def test_assessment_evaluation_service(app):
    """Verifies end-to-end evaluation engine across streams and marks."""
    with app.app_context():
        payload = {
            'stream': 'Science',
            'subject_marks': {
                'Mathematics': 92,
                'Physics': 88,
                'Chemistry': 84,
                'Computer Science': 96
            },
            'interests': ['Technology', 'Programming'],
            'preferred_district': 'Chennai'
        }
        res = AssessmentService.evaluate_student_assessment(payload)

        assert res['academic']['stream'] == 'Science'
        assert res['academic']['percentage'] == 90.0
        assert res['academic']['tnea_cutoff']['formula_cutoff'] == 89.0  # 92/2=46, 88/4=22, 84/4=21 -> 89.0
        assert len(res['recommended_courses']) > 0
        assert any('Computer' in c['course_name'] or 'BCA' in c['course_name'] for c in res['recommended_courses'])
        assert 'career_pathways' in res
        assert len(res['career_pathways']['possible_careers']) > 0
        assert len(res['career_pathways']['higher_studies']) > 0
        assert len(res['career_pathways']['key_skills']) > 0


def test_ai_counselor_service_fallback():
    """Tests the AI Education Counselor fallback engine when GEMINI_API_KEY is not set."""
    # 1. Greeting
    res_greet = AICounselorService.get_counselor_response("Hello")
    assert res_greet['success'] is True
    assert "EduVerse AI Counselor" in res_greet['response']

    # 2. Cutoff query
    res_cutoff = AICounselorService.get_counselor_response("How is TNEA engineering cutoff calculated?")
    assert res_cutoff['success'] is True
    assert "Mathematics" in res_cutoff['response']
    assert "tneaonline.org" in res_cutoff['response']

    # 3. Commerce inquiry
    res_comm = AICounselorService.get_counselor_response("What are my options after 12th commerce?")
    assert res_comm['success'] is True
    assert "B.Com" in res_comm['response'] or "BBA" in res_comm['response']

    # 4. BCA inquiry
    res_bca = AICounselorService.get_counselor_response("What careers can I pursue after BCA?")
    assert res_bca['success'] is True
    assert "MCA" in res_bca['response'] or "Software" in res_bca['response']


def test_student_profile_model(app):
    """Tests StudentProfile persistence and helper methods."""
    with app.app_context():
        user = User(name='Test Student', email='teststudent@example.com', role='student')
        user.set_password('Pass1234!')
        db.session.add(user)
        db.session.commit()

        profile = StudentProfile(
            user_id=user.id,
            stream='Science',
            phone='9876543210',
            location='Madurai',
            school='Model Higher Secondary School'
        )
        profile.set_subject_marks({'Mathematics': 95, 'Physics': 90})
        profile.set_interests(['Technology', 'Engineering'])
        profile.total_marks = 185
        profile.percentage = 92.5
        profile.tnea_cutoff = 90.0

        db.session.add(profile)
        db.session.commit()

        loaded = StudentProfile.query.filter_by(user_id=user.id).first()
        assert loaded is not None
        assert loaded.stream == 'Science'
        assert loaded.get_subject_marks() == {'Mathematics': 95, 'Physics': 90}
        assert loaded.get_interests() == ['Technology', 'Engineering']
        assert loaded.to_dict()['phone'] == '9876543210'


def test_student_web_routes(app, student_client):
    """Tests the student web routes: dashboard, profile, assessment, results, careers, contact."""
    guest_client = app.test_client()

    # 1. Dashboard (guest and student)
    res_guest_dash = guest_client.get('/student/dashboard')
    assert res_guest_dash.status_code == 200
    assert b"12th Standard Guidance Hub" in res_guest_dash.data

    res_student_dash = student_client.get('/student/dashboard')
    assert res_student_dash.status_code == 200

    # 2. Profile
    res_profile_guest = guest_client.get('/student/profile')
    assert res_profile_guest.status_code == 302  # redirects to login

    res_profile_auth = student_client.get('/student/profile')
    assert res_profile_auth.status_code == 200
    assert b"Student Academic" in res_profile_auth.data

    # 3. Assessment form
    res_assessment_page = guest_client.get('/student/assessment')
    assert res_assessment_page.status_code == 200
    assert b"Select Your 12th Academic Stream" in res_assessment_page.data

    # 4. Careers guide
    res_careers = guest_client.get('/student/careers')
    assert res_careers.status_code == 200
    assert b"Career Pathways & Higher Studies Guide" in res_careers.data
    assert b"BCA" in res_careers.data
    assert b"MCA" in res_careers.data

    # 5. Contact page with team credits
    res_contact = guest_client.get('/contact')
    assert res_contact.status_code == 200
    assert b"R. Priyadharshini" in res_contact.data
    assert b"9525621125" in res_contact.data
    assert b"T. Priyanka" in res_contact.data
    assert b"9525621126" in res_contact.data
    assert b"Department of Master of Computer Applications (MCA)" in res_contact.data


def test_contact_query_submission(client, app):
    """Tests submitting a query via the contact form and verifying it in database."""
    with app.app_context():
        # Submit contact form
        post_data = {
            'name': 'Priyanka Student',
            'email': 'priyanka_student@example.com',
            'phone': '9876543210',
            'category': 'Course Information',
            'message': 'Which colleges offer BCA with AI specialization in Coimbatore?'
        }
        res = client.post('/contact', data=post_data, follow_redirects=True)
        assert res.status_code == 200
        assert b"submitted successfully" in res.data

        # Verify saved in StudentQuery table
        query_saved = StudentQuery.query.filter_by(email='priyanka_student@example.com').first()
        assert query_saved is not None
        assert query_saved.student_name == 'Priyanka Student'
        assert query_saved.status == 'PENDING'


def test_student_api_endpoints(client):
    """Tests student REST APIs: assessment, advisor, recommendations."""
    # 1. Assessment API
    eval_payload = {
        'stream': 'Science',
        'subject_marks': {
            'Mathematics': 85,
            'Physics': 80,
            'Chemistry': 75,
            'Computer Science': 90
        },
        'interests': ['Technology'],
        'preferred_district': 'Coimbatore'
    }
    res_eval = client.post('/api/assessment', json=eval_payload)
    assert res_eval.status_code == 200
    data = res_eval.get_json()
    assert data['success'] is True
    assert 'academic' in data['data']
    assert data['data']['academic']['percentage'] == 82.5

    # 2. AI Counselor API
    res_advisor = client.post('/api/ai/advisor', json={'message': 'Tell me about engineering cutoffs'})
    assert res_advisor.status_code == 200
    adv_data = res_advisor.get_json()
    assert adv_data['success'] is True
    assert len(adv_data['response']) > 10

    # 3. Recommendations API
    res_recs = client.post('/api/recommendations', json=eval_payload)
    assert res_recs.status_code == 200
    recs_data = res_recs.get_json()
    assert recs_data['success'] is True
    assert 'recommended_courses' in recs_data
    assert 'matched_colleges' in recs_data
