from flask import Blueprint, render_template, request, jsonify
from app import csrf
from app.services.comparison_service import ComparisonService

comparison_bp = Blueprint('comparison', __name__)


@comparison_bp.route('/compare')
def compare_page():
    """Renders the side-by-side college comparison matrix page."""
    data = ComparisonService.get_comparison_data()
    return render_template('compare.html', **data)


# ==========================================
# REST API ENDPOINTS
# ==========================================

@comparison_bp.route('/api/compare', methods=['GET'])
def api_get_compare():
    """Retrieves the current comparison matrix."""
    data = ComparisonService.get_comparison_data()
    return jsonify({
        'success': True,
        **data
    }), 200


@comparison_bp.route('/api/compare', methods=['POST'])
@csrf.exempt
def api_add_compare():
    """Adds a college to the comparison list."""
    payload = request.get_json() or {}
    college_id = payload.get('college_id')

    if not college_id or not str(college_id).isdigit():
        return jsonify({
            'success': False,
            'error': {
                'code': 'INVALID_COLLEGE_ID',
                'message': 'Valid numeric college_id is required.'
            }
        }), 400

    success, message, count = ComparisonService.add_college(int(college_id))
    if not success:
        return jsonify({
            'success': False,
            'compare_count': count,
            'error': {
                'code': 'COMPARISON_LIMIT_OR_DUPLICATE',
                'message': message
            }
        }), 400

    return jsonify({
        'success': True,
        'message': message,
        'compare_count': count
    }), 200


@comparison_bp.route('/api/compare/<int:college_id>', methods=['DELETE'])
@csrf.exempt
def api_remove_compare(college_id):
    """Removes a college from comparison."""
    success, message, count = ComparisonService.remove_college(college_id)
    if not success:
        return jsonify({
            'success': False,
            'error': {
                'code': 'NOT_FOUND_IN_COMPARISON',
                'message': message
            }
        }), 404

    return jsonify({
        'success': True,
        'message': message,
        'compare_count': count
    }), 200


@comparison_bp.route('/api/compare/clear', methods=['POST'])
@csrf.exempt
def api_clear_compare():
    """Clears all colleges from comparison matrix."""
    success, message = ComparisonService.clear_all()
    return jsonify({
        'success': True,
        'message': message,
        'compare_count': 0
    }), 200
