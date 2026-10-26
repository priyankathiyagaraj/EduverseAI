from flask import Blueprint, render_template, request, jsonify
from app import csrf
from app.services.college_service import CollegeService
from app.services.recommendation_service import RecommendationService

recommendations_bp = Blueprint('recommendations', __name__)


@recommendations_bp.route('/recommendations')
def recommendations_page():
    """Renders the AI Recommendation interface."""
    courses = CollegeService.get_all_courses()
    districts = CollegeService.get_all_districts()
    college_types = CollegeService.get_all_college_types()
    facilities = CollegeService.get_all_facilities()

    return render_template(
        'recommendations.html',
        courses=courses,
        districts=districts,
        college_types=college_types,
        facilities=facilities
    )


@recommendations_bp.route('/api/recommend', methods=['POST'])
@csrf.exempt
def api_recommend():
    """
    POST /api/recommend
    Body:
    {
        "course": "MCA",
        "state": "Tamil Nadu",
        "district": "Chennai",
        "city": "",
        "budget": 100000,
        "college_type": "",
        "facilities": ["Hostel", "Placement Cell"]
    }
    """
    try:
        payload = request.get_json() or {}
        results = RecommendationService.get_recommendations(payload, top_k=12)

        return jsonify({
            'success': True,
            **results
        }), 200

    except ValueError as ve:
        return jsonify({
            'success': False,
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': str(ve)
            }
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'RECOMMENDER_ERROR',
                'message': str(e)
            }
        }), 500


@recommendations_bp.route('/api/recommend/courses', methods=['POST'])
@csrf.exempt
def api_recommend_courses():
    """
    POST /api/recommend/courses
    Body:
    {
        "marks_12th": 85.5,
        "stream": "Science (Maths)",
        "subject_marks": {
            "mathematics": 90,
            "computer_science": 92,
            "physics": 82
        },
        "interests": ["Software & AI", "Engineering & Technology"]
    }
    """
    try:
        from app.services.course_recommendation_service import CourseRecommendationService
        payload = request.get_json() or {}
        results = CourseRecommendationService.recommend_courses_ai(payload)
        return jsonify({
            'success': True,
            **results
        }), 200
    except ValueError as ve:
        return jsonify({
            'success': False,
            'error': {'code': 'VALIDATION_ERROR', 'message': str(ve)}
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {'code': 'RECOMMENDER_ERROR', 'message': str(e)}
        }), 500


@recommendations_bp.route('/api/courses/discover', methods=['POST'])
@csrf.exempt
def api_discover_courses():
    """
    POST /api/courses/discover
    Body:
    {
        "marks_12th": 60,
        "stream": "Commerce",
        "category": "All",
        "career_field": "Finance"
    }
    """
    try:
        from app.services.course_recommendation_service import CourseRecommendationService
        payload = request.get_json() or {}
        results = CourseRecommendationService.discover_courses_normal(payload)
        return jsonify({
            'success': True,
            **results
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {'code': 'DISCOVERY_ERROR', 'message': str(e)}
        }), 500
