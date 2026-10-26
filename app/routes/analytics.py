from flask import Blueprint, render_template, jsonify
from app.services.analytics_service import AnalyticsService

analytics_bp = Blueprint('analytics', __name__)


@analytics_bp.route('/analytics')
def analytics_page():
    """Renders the live Analytics Dashboard page."""
    data = AnalyticsService.get_analytics_metrics()
    return render_template('analytics.html', analytics=data)


@analytics_bp.route('/api/analytics', methods=['GET'])
def api_analytics():
    """Returns analytics data as JSON for Chart.js."""
    try:
        data = AnalyticsService.get_analytics_metrics()
        return jsonify({
            'success': True,
            **data
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'ANALYTICS_ERROR',
                'message': str(e)
            }
        }), 500
