from flask import Blueprint, render_template, request, jsonify, abort
from app.services.college_service import CollegeService

colleges_bp = Blueprint('colleges', __name__)


@colleges_bp.route('/explore')
def explore():
    """Renders the College Explorer page with server-side preloaded filter choices."""
    districts = CollegeService.get_all_districts()
    courses = CollegeService.get_all_courses()
    college_types = CollegeService.get_all_college_types()
    facilities = CollegeService.get_all_facilities()

    # Read initial URL query parameters if arriving from Home search
    initial_query = request.args.get('q', '').strip()
    initial_course = request.args.get('course', '').strip()
    initial_district = request.args.get('district', '').strip()

    return render_template(
        'explore.html',
        districts=districts,
        courses=courses,
        college_types=college_types,
        facilities=facilities,
        initial_query=initial_query,
        initial_course=initial_course,
        initial_district=initial_district
    )


@colleges_bp.route('/college/<int:id>')
def college_detail(id):
    """Renders the comprehensive profile for a specific college."""
    college = CollegeService.get_college_by_id(id)
    if not college:
        abort(404)
    return render_template('college_detail.html', college=college.to_dict(include_details=True), raw_college=college)


@colleges_bp.route('/map')
def map_page():
    """Renders the dedicated interactive Leaflet map of Tamil Nadu colleges."""
    colleges = CollegeService.search_colleges(per_page=1200)['colleges']
    return render_template('map.html', colleges=colleges)


# ==========================================
# REST API ENDPOINTS
# ==========================================

@colleges_bp.route('/api/colleges', methods=['GET'])
def api_colleges():
    """
    JSON API for paginated and filtered college search.
    Supports: query, course, district, city, college_type, max_fee, facilities, sort, page, per_page
    """
    try:
        query = request.args.get('query', '').strip()
        course = request.args.get('course', '').strip()
        district = request.args.get('district', '').strip()
        city = request.args.get('city', '').strip()
        college_type = request.args.get('college_type', '').strip()
        autonomous = request.args.get('autonomous', '').strip()
        data_status = request.args.get('data_status', '').strip()

        max_fee_raw = request.args.get('max_fee')
        max_fee = float(max_fee_raw) if max_fee_raw and max_fee_raw.strip() else None

        # Facilities can be comma-separated or multiple params
        facilities_raw = request.args.getlist('facilities')
        facilities = []
        for f in facilities_raw:
            facilities.extend([item.strip() for item in f.split(',') if item.strip()])

        sort_by = request.args.get('sort', 'name')
        page = max(1, int(request.args.get('page', 1)))
        per_page = min(50, max(1, int(request.args.get('per_page', 9))))

        result = CollegeService.search_colleges(
            query=query,
            course=course,
            district=district,
            city=city,
            college_type=college_type,
            autonomous=autonomous,
            data_status=data_status,
            max_fee=max_fee,
            facilities=facilities,
            sort_by=sort_by,
            page=page,
            per_page=per_page
        )

        return jsonify({
            'success': True,
            'colleges': result['colleges'],
            'pagination': result['pagination']
        }), 200

    except ValueError as ve:
        return jsonify({
            'success': False,
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': f"Invalid numerical parameter: {str(ve)}"
            }
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'SERVER_ERROR',
                'message': str(e)
            }
        }), 500


@colleges_bp.route('/api/colleges/<int:id>', methods=['GET'])
def api_college_detail(id):
    """Returns single college profile as JSON."""
    college = CollegeService.get_college_by_id(id)
    if not college:
        return jsonify({
            'success': False,
            'error': {
                'code': 'NOT_FOUND',
                'message': f"College with ID {id} was not found."
            }
        }), 404

    return jsonify({
        'success': True,
        'college': college.to_dict(include_details=True)
    }), 200


@colleges_bp.route('/api/courses', methods=['GET'])
def api_courses():
    """Returns unique courses available in the system."""
    return jsonify({
        'success': True,
        'courses': CollegeService.get_all_courses()
    }), 200


@colleges_bp.route('/api/districts', methods=['GET'])
def api_districts():
    """Returns all 38 Tamil Nadu districts with detailed college availability metadata."""
    districts_list = CollegeService.get_all_districts()
    detailed = CollegeService.get_districts_detailed()
    return jsonify({
        'success': True,
        'total_districts': len(districts_list),
        'districts': districts_list,
        'details': detailed
    }), 200


@colleges_bp.route('/api/facilities', methods=['GET'])
def api_facilities():
    """Returns unique facilities cataloged."""
    return jsonify({
        'success': True,
        'facilities': CollegeService.get_all_facilities()
    }), 200


@colleges_bp.route('/api/college-types', methods=['GET'])
def api_college_types():
    """Returns controlled college types, autonomous options, and legacy types."""
    return jsonify({
        'success': True,
        'primary_college_types': [
            {'code': 'GOVERNMENT', 'label': 'Government'},
            {'code': 'GOVERNMENT_AIDED', 'label': 'Government-Aided'},
            {'code': 'SELF_FINANCING', 'label': 'Self-Financing'},
            {'code': 'OTHER', 'label': 'Other / Central / Deemed'}
        ],
        'primary_types': ['GOVERNMENT', 'GOVERNMENT_AIDED', 'SELF_FINANCING', 'OTHER'],
        'autonomous_statuses': ['AUTONOMOUS', 'NON_AUTONOMOUS'],
        'display_types': CollegeService.get_all_college_types()
    }), 200
