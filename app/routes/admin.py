from datetime import datetime, timezone
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, abort
from app import db, csrf
from app.models.college import College
from app.models.course import Course
from app.models.facility import Facility
from app.models.district import District
from app.models.student_query import StudentQuery
from app.utils.decorators import admin_required
from app.utils.validators import validate_college_payload

admin_bp = Blueprint('admin', __name__)


# ==========================================
# WEB ADMIN VIEWS
# ==========================================

@admin_bp.route('/admin')
@admin_bp.route('/admin/')
@admin_required
def dashboard():
    """Admin management dashboard listing all indexed institutions and student queries."""
    page = max(1, int(request.args.get('page', 1)))
    per_page = 15
    query = request.args.get('q', '').strip()

    stmt = College.query
    if query:
        term = f"%{query}%"
        stmt = stmt.filter(
            db.or_(
                College.name.ilike(term),
                College.district.ilike(term),
                College.city.ilike(term),
                College.code.ilike(term)
            )
        )

    pagination = stmt.order_by(College.name.asc()).paginate(page=page, per_page=per_page, error_out=False)

    total_colleges = College.query.count()
    total_courses = Course.query.count()
    verified_count = College.query.filter_by(data_status='VERIFIED').count()
    sample_count = College.query.filter_by(data_status='SAMPLE').count()
    verified_website_count = College.query.filter_by(website_status='VERIFIED').count()

    # Dynamic Student Overview & Analytics from Database
    from app.services.student_analytics_service import (
        get_student_overview_stats,
        get_login_chart_data,
        get_feedback_analytics
    )
    student_stats = get_student_overview_stats()
    feedback_stats = get_feedback_analytics()
    chart_7d = get_login_chart_data('7d')

    recent_queries = StudentQuery.query.order_by(StudentQuery.created_at.desc()).limit(6).all()
    from app.models.student_feedback import StudentFeedback
    recent_feedback = StudentFeedback.query.order_by(StudentFeedback.created_at.desc()).limit(6).all()

    return render_template(
        'admin/dashboard.html',
        colleges=pagination.items,
        pagination=pagination,
        search_query=query,
        student_stats=student_stats,
        feedback_stats=feedback_stats,
        login_chart=chart_7d,
        recent_feedback=recent_feedback,
        stats={
            'total_colleges': total_colleges,
            'total_courses': total_courses,
            'verified_count': verified_count,
            'sample_count': sample_count,
            'verified_website_count': verified_website_count,
            'pending_queries_count': student_stats['pending_queries'],
            'total_queries_count': student_stats['total_queries'],
            'recent_queries': recent_queries
        }
    )


@admin_bp.route('/admin/colleges/new', methods=['GET', 'POST'])
@admin_required
def new_college():
    """Create new college record with courses and facilities."""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        code = request.form.get('code', '').strip()
        state = request.form.get('state', 'Tamil Nadu').strip()
        district = request.form.get('district', '').strip()
        city = request.form.get('city', '').strip()
        college_type = request.form.get('college_type', '').strip()
        address = request.form.get('address', '').strip()
        lat = request.form.get('latitude', '').strip()
        lng = request.form.get('longitude', '').strip()
        website = request.form.get('website', '').strip()
        official_website_url = request.form.get('official_website_url', '').strip() or website
        website_status = request.form.get('website_status', '').strip()

        sanitized_website = College.sanitize_url(official_website_url) if official_website_url else None
        if not sanitized_website:
            final_status = 'MISSING' if website_status != 'BROKEN' else 'BROKEN'
        else:
            final_status = website_status or 'VERIFIED'

        description = request.form.get('description', '').strip()
        source_url = request.form.get('source_url', '').strip()
        data_status = request.form.get('data_status', 'SAMPLE').strip()

        district_id_val = request.form.get('district_id')
        district_name = request.form.get('district', '').strip()
        from app.utils.district_normalizer import resolve_district_entity
        dist_entity = resolve_district_entity(district_id_val or district_name)
        resolved_district_name = dist_entity.name if dist_entity else district_name

        valid, err = validate_college_payload({
            'name': name,
            'district': resolved_district_name,
            'city': city,
            'college_type': college_type,
            'latitude': lat,
            'longitude': lng
        })
        if not valid:
            flash(err, 'error')
            districts = District.query.order_by(District.name.asc()).all()
            return render_template('admin/college_form.html', action='new', college={}, districts=districts)

        primary_college_type = request.form.get('primary_college_type', '').strip()
        autonomous_status = request.form.get('autonomous_status', '').strip()

        if not primary_college_type or primary_college_type == 'UNKNOWN':
            ct_up = college_type.upper()
            if 'AIDED' in ct_up:
                primary_college_type = 'GOVERNMENT_AIDED'
            elif 'GOVERNMENT' in ct_up or 'GOVT' in ct_up:
                primary_college_type = 'GOVERNMENT'
            elif 'SELF' in ct_up or 'PRIVATE' in ct_up:
                primary_college_type = 'SELF_FINANCING'
            elif 'UNIVERSITY' in ct_up or 'DEEMED' in ct_up:
                primary_college_type = 'OTHER'
            else:
                primary_college_type = 'UNKNOWN'

        if not autonomous_status or autonomous_status == 'UNKNOWN':
            autonomous_status = 'AUTONOMOUS' if 'AUTONOMOUS' in college_type.upper() else 'NON_AUTONOMOUS'

        college = College(
            name=name,
            normalized_name=College.normalize_name_static(name),
            code=code or None,
            state=state or 'Tamil Nadu',
            district_id=dist_entity.id if dist_entity else None,
            district=resolved_district_name,
            city=city,
            college_type=college_type,
            primary_college_type=primary_college_type,
            autonomous_status=autonomous_status,
            address=address or None,
            latitude=float(lat) if lat else None,
            longitude=float(lng) if lng else None,
            official_website=sanitized_website,
            official_website_url=sanitized_website,
            website_status=final_status,
            website=sanitized_website,
            description=description or None,
            source_url=source_url or None,
            data_status=data_status,
            last_updated=datetime.now(timezone.utc)
        )
        db.session.add(college)
        db.session.flush()

        # Add course if provided
        course_name = request.form.get('initial_course_name', '').strip()
        course_fee = request.form.get('initial_course_fee', '').strip()
        course_cat = request.form.get('initial_course_category', '').strip()

        if course_name:
            crs = Course(
                college_id=college.id,
                course_name=course_name,
                course_category=course_cat or 'Postgraduate',
                annual_fee=float(course_fee) if course_fee else None
            )
            db.session.add(crs)

        # Add facilities if provided
        facilities_raw = request.form.get('facilities_csv', '').strip()
        if facilities_raw:
            for fac in facilities_raw.split(','):
                if fac.strip():
                    db.session.add(Facility(college_id=college.id, facility_name=fac.strip()))

        db.session.commit()
        flash(f"Successfully created institution '{college.name}'.", 'success')
        return redirect(url_for('admin.dashboard'))

    districts = District.query.order_by(District.name.asc()).all()
    return render_template('admin/college_form.html', action='new', college={}, districts=districts)


@admin_bp.route('/admin/colleges/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_college(id):
    """Edit existing college profile, fee structure, facilities, and data status."""
    college = College.query.get_or_404(id)

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        code = request.form.get('code', '').strip()
        district = request.form.get('district', '').strip()
        city = request.form.get('city', '').strip()
        college_type = request.form.get('college_type', '').strip()
        address = request.form.get('address', '').strip()
        lat = request.form.get('latitude', '').strip()
        lng = request.form.get('longitude', '').strip()
        website = request.form.get('website', '').strip()
        official_website_url = request.form.get('official_website_url', '').strip() or website
        website_status = request.form.get('website_status', '').strip()

        sanitized_website = College.sanitize_url(official_website_url) if official_website_url else None
        if not sanitized_website:
            final_status = 'MISSING' if website_status != 'BROKEN' else 'BROKEN'
        else:
            final_status = website_status or 'VERIFIED'

        description = request.form.get('description', '').strip()
        source_url = request.form.get('source_url', '').strip()
        data_status = request.form.get('data_status', 'SAMPLE').strip()

        district_id_val = request.form.get('district_id')
        district_name = request.form.get('district', '').strip()
        from app.utils.district_normalizer import resolve_district_entity
        dist_entity = resolve_district_entity(district_id_val or district_name)
        resolved_district_name = dist_entity.name if dist_entity else (district_name or college.district)

        valid, err = validate_college_payload({
            'name': name,
            'district': resolved_district_name,
            'city': city,
            'college_type': college_type,
            'latitude': lat,
            'longitude': lng
        })
        if not valid:
            flash(err, 'error')
            districts = District.query.order_by(District.name.asc()).all()
            return render_template('admin/college_form.html', action='edit', college=college.to_dict(include_details=True), districts=districts)

        primary_college_type = request.form.get('primary_college_type', '').strip()
        autonomous_status = request.form.get('autonomous_status', '').strip()

        college.name = name
        college.normalized_name = College.normalize_name_static(name)
        college.code = code or None
        if dist_entity:
            college.district_id = dist_entity.id
        college.district = resolved_district_name
        college.city = city
        college.college_type = college_type
        if primary_college_type:
            college.primary_college_type = primary_college_type
        if autonomous_status:
            college.autonomous_status = autonomous_status
        college.address = address or None
        college.latitude = float(lat) if lat else None
        college.longitude = float(lng) if lng else None
        college.official_website = sanitized_website
        college.official_website_url = sanitized_website
        college.website_status = final_status
        college.website = sanitized_website
        college.description = description or None
        college.source_url = source_url or None
        college.data_status = data_status
        college.last_updated = datetime.now(timezone.utc)

        # Optional new course addition from edit page
        new_course_name = request.form.get('new_course_name', '').strip()
        new_course_fee = request.form.get('new_course_fee', '').strip()
        if new_course_name:
            crs = Course(
                college_id=college.id,
                course_name=new_course_name,
                annual_fee=float(new_course_fee) if new_course_fee else None
            )
            db.session.add(crs)

        # Optional facilities update
        new_facilities = request.form.get('facilities_csv', '').strip()
        if new_facilities:
            # Replace existing facilities
            Facility.query.filter_by(college_id=college.id).delete()
            for fac in new_facilities.split(','):
                if fac.strip():
                    db.session.add(Facility(college_id=college.id, facility_name=fac.strip()))

        db.session.commit()
        flash(f"Updated '{college.name}' successfully.", 'success')
        return redirect(url_for('admin.dashboard'))

    districts = District.query.order_by(District.name.asc()).all()
    return render_template('admin/college_form.html', action='edit', college=college.to_dict(include_details=True), districts=districts)


@admin_bp.route('/admin/colleges/<int:id>/delete', methods=['POST'])
@admin_required
def delete_college(id):
    """Deletes college with confirmed POST request."""
    college = College.query.get_or_404(id)
    c_name = college.name
    db.session.delete(college)
    db.session.commit()
    flash(f"Institution '{c_name}' has been deleted.", 'info')
    return redirect(url_for('admin.dashboard'))


# ==========================================
# REST API FOR ADMIN CRUD
# ==========================================

@admin_bp.route('/api/admin/colleges', methods=['POST'])
@admin_required
@csrf.exempt
def api_create_college():
    data = request.get_json() or {}
    valid, err = validate_college_payload(data)
    if not valid:
        return jsonify({
            'success': False,
            'error': {'code': 'VALIDATION_ERROR', 'message': err}
        }), 400

    raw_url = data.get('official_website_url') or data.get('website')
    sanitized_url = College.sanitize_url(raw_url) if raw_url else None
    stat = data.get('website_status')
    if not sanitized_url:
        website_status = 'MISSING' if stat != 'BROKEN' else 'BROKEN'
    else:
        website_status = stat or 'VERIFIED'

    college = College(
        name=data['name'],
        code=data.get('code'),
        state=data.get('state', 'Tamil Nadu'),
        district=data['district'],
        city=data['city'],
        college_type=data['college_type'],
        address=data.get('address'),
        latitude=float(data['latitude']) if data.get('latitude') else None,
        longitude=float(data['longitude']) if data.get('longitude') else None,
        official_website_url=sanitized_url,
        website_status=website_status,
        website=sanitized_url,
        description=data.get('description'),
        source_url=data.get('source_url'),
        data_status=data.get('data_status', 'SAMPLE'),
        last_updated=datetime.now(timezone.utc)
    )
    db.session.add(college)
    db.session.flush()

    for crs in data.get('courses', []):
        course = Course(
            college_id=college.id,
            course_name=crs.get('name'),
            annual_fee=float(crs['fee']) if crs.get('fee') is not None else None,
            duration_years=float(crs.get('duration', 2.0))
        )
        db.session.add(course)

    for fac in data.get('facilities', []):
        db.session.add(Facility(college_id=college.id, facility_name=fac))

    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'College created successfully.',
        'college': college.to_dict(include_details=True)
    }), 201


@admin_bp.route('/api/admin/colleges/<int:id>', methods=['PUT'])
@admin_required
@csrf.exempt
def api_update_college(id):
    college = db.session.get(College, id)
    if not college:
        return jsonify({
            'success': False,
            'error': {'code': 'NOT_FOUND', 'message': 'College not found.'}
        }), 404

    data = request.get_json() or {}
    if 'name' in data: college.name = data['name']
    if 'district' in data: college.district = data['district']
    if 'city' in data: college.city = data['city']
    if 'college_type' in data: college.college_type = data['college_type']
    if 'address' in data: college.address = data['address']
    if 'latitude' in data: college.latitude = float(data['latitude']) if data['latitude'] is not None else None
    if 'longitude' in data: college.longitude = float(data['longitude']) if data['longitude'] is not None else None
    if 'official_website_url' in data or 'website' in data:
        raw_url = data.get('official_website_url') or data.get('website')
        sanitized_url = College.sanitize_url(raw_url) if raw_url else None
        college.official_website_url = sanitized_url
        college.website = sanitized_url
        if sanitized_url:
            if 'website_status' not in data:
                college.website_status = 'VERIFIED'
        else:
            college.website_status = 'MISSING'
    if 'website_status' in data:
        college.website_status = data['website_status']
    if 'description' in data: college.description = data['description']
    if 'source_url' in data: college.source_url = data['source_url']
    if 'data_status' in data: college.data_status = data['data_status']

    college.last_updated = datetime.now(timezone.utc)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': 'College updated successfully.',
        'college': college.to_dict(include_details=True)
    }), 200


@admin_bp.route('/api/admin/colleges/<int:id>', methods=['DELETE'])
@admin_required
@csrf.exempt
def api_delete_college(id):
    college = db.session.get(College, id)
    if not college:
        return jsonify({
            'success': False,
            'error': {'code': 'NOT_FOUND', 'message': 'College not found.'}
        }), 404

    c_name = college.name
    db.session.delete(college)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': f"College '{c_name}' deleted successfully."
    }), 200


# ==========================================
# ADMIN STUDENT QUERY MANAGEMENT
# ==========================================

@admin_bp.route('/admin/queries')
@admin_required
def admin_queries():
    """
    Dedicated view for managing, filtering, searching, and responding
    to incoming student queries.
    """
    page = max(1, int(request.args.get('page', 1)))
    per_page = 15
    q_search = request.args.get('q', '').strip()
    status_filter = request.args.get('status', '').strip().upper()
    category_filter = request.args.get('category', '').strip()

    stmt = StudentQuery.query

    if q_search:
        term = f"%{q_search}%"
        stmt = stmt.filter(
            db.or_(
                StudentQuery.student_name.ilike(term),
                StudentQuery.email.ilike(term),
                StudentQuery.message.ilike(term)
            )
        )

    if status_filter and status_filter != 'ALL':
        stmt = stmt.filter(StudentQuery.status == status_filter)

    if category_filter and category_filter != 'ALL':
        stmt = stmt.filter(StudentQuery.category == category_filter)

    pagination = stmt.order_by(StudentQuery.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    pending_count = StudentQuery.query.filter_by(status='PENDING').count()
    in_progress_count = StudentQuery.query.filter_by(status='IN_PROGRESS').count()
    resolved_count = StudentQuery.query.filter_by(status='RESOLVED').count()
    total_count = StudentQuery.query.count()

    # Feedback Management support
    from app.models.student_feedback import StudentFeedback
    from app.services.student_analytics_service import get_feedback_analytics
    feedback_stats = get_feedback_analytics()
    active_tab = request.args.get('tab', 'queries')

    feedback_stmt = StudentFeedback.query
    if q_search and active_tab == 'feedback':
        term = f"%{q_search}%"
        feedback_stmt = feedback_stmt.filter(
            db.or_(
                StudentFeedback.student_name.ilike(term),
                StudentFeedback.email.ilike(term),
                StudentFeedback.feedback_message.ilike(term)
            )
        )
    feedback_pagination = feedback_stmt.order_by(StudentFeedback.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return render_template(
        'admin/queries.html',
        queries=pagination.items,
        pagination=pagination,
        active_tab=active_tab,
        feedback_items=feedback_pagination.items,
        feedback_pagination=feedback_pagination,
        feedback_stats=feedback_stats,
        search_query=q_search,
        status_filter=status_filter,
        category_filter=category_filter,
        categories=StudentQuery.CATEGORIES,
        statuses=StudentQuery.STATUSES,
        counts={
            'pending': pending_count,
            'in_progress': in_progress_count,
            'resolved': resolved_count,
            'total': total_count
        }
    )


@admin_bp.route('/admin/feedback/<int:id>/delete', methods=['POST'])
@admin_required
def admin_delete_feedback(id):
    """Deletes spam or inappropriate student feedback."""
    from app.models.student_feedback import StudentFeedback
    fb = StudentFeedback.query.get_or_404(id)
    fid = fb.id
    db.session.delete(fb)
    db.session.commit()
    flash(f"Feedback #{fid} has been permanently deleted.", 'info')
    return redirect(url_for('admin.admin_queries', tab='feedback'))


@admin_bp.route('/admin/queries/<int:id>/respond', methods=['POST'])
@admin_required
def admin_respond_query(id):
    """Saves an administrative response and updates the query status."""
    query = StudentQuery.query.get_or_404(id)
    response_text = request.form.get('admin_response', '').strip()
    new_status = request.form.get('status', 'RESOLVED').strip()

    if not response_text:
        flash("Response message cannot be empty.", 'error')
        return redirect(url_for('admin.admin_queries'))

    query.admin_response = response_text
    query.status = new_status if new_status in StudentQuery.STATUSES else 'RESOLVED'
    query.updated_at = datetime.now(timezone.utc)
    db.session.commit()

    flash(f"Response saved for Ticket #{query.id} ({query.student_name}). Status: {query.status}.", 'success')
    return redirect(url_for('admin.admin_queries'))


@admin_bp.route('/admin/queries/<int:id>/status', methods=['POST'])
@admin_required
def admin_update_query_status(id):
    """Directly changes the workflow status of a student query."""
    query = StudentQuery.query.get_or_404(id)
    new_status = request.form.get('status', '').strip().upper()

    if new_status in StudentQuery.STATUSES:
        query.status = new_status
        query.updated_at = datetime.now(timezone.utc)
        db.session.commit()
        flash(f"Ticket #{query.id} status updated to {new_status}.", 'info')
    else:
        flash("Invalid status specified.", 'error')

    return redirect(url_for('admin.admin_queries'))


@admin_bp.route('/admin/queries/<int:id>/delete', methods=['POST'])
@admin_required
def admin_delete_query(id):
    """Deletes spam or inappropriate student query."""
    query = StudentQuery.query.get_or_404(id)
    qid = query.id
    db.session.delete(query)
    db.session.commit()
    flash(f"Query Ticket #{qid} has been permanently deleted.", 'info')
    return redirect(url_for('admin.admin_queries'))


# REST API Endpoints for Student Analytics, Login Charts, and Feedback
@admin_bp.route('/api/admin/student-overview', methods=['GET'])
@admin_required
def api_student_overview():
    """Returns dynamic student overview metrics."""
    from app.services.student_analytics_service import get_student_overview_stats
    stats = get_student_overview_stats()
    return jsonify({
        'success': True,
        'stats': stats
    }), 200


@admin_bp.route('/api/admin/analytics/logins', methods=['GET'])
@admin_required
def api_login_analytics():
    """Returns aggregated login counts by day/period for Chart.js."""
    timeframe = request.args.get('timeframe', '7d').lower()
    from app.services.student_analytics_service import get_login_chart_data
    chart_data = get_login_chart_data(timeframe)
    return jsonify({
        'success': True,
        'chart': chart_data
    }), 200


@admin_bp.route('/api/admin/feedback', methods=['GET'])
@admin_required
def api_list_feedback():
    """Lists student ratings and feedback submissions."""
    from app.services.student_analytics_service import get_feedback_analytics
    analytics = get_feedback_analytics()
    return jsonify({
        'success': True,
        'analytics': analytics
    }), 200


@admin_bp.route('/api/admin/feedback/<int:id>', methods=['DELETE'])
@admin_required
@csrf.exempt
def api_delete_feedback(id):
    """Deletes a feedback item via REST API."""
    from app.models.student_feedback import StudentFeedback
    fb = StudentFeedback.query.get_or_404(id)
    db.session.delete(fb)
    db.session.commit()
    return jsonify({
        'success': True,
        'message': f"Feedback #{id} deleted successfully."
    }), 200


# REST API Endpoints for Student Queries
@admin_bp.route('/api/admin/queries', methods=['GET'])
@admin_required
def api_list_queries():
    """Lists student queries with optional filtering for administrative dashboard widgets."""
    status_filter = request.args.get('status', '').strip().upper()
    category_filter = request.args.get('category', '').strip()

    stmt = StudentQuery.query
    if status_filter and status_filter != 'ALL':
        stmt = stmt.filter(StudentQuery.status == status_filter)
    if category_filter and category_filter != 'ALL':
        stmt = stmt.filter(StudentQuery.category == category_filter)

    queries = stmt.order_by(StudentQuery.created_at.desc()).limit(100).all()
    pending_count = StudentQuery.query.filter_by(status='PENDING').count()

    return jsonify({
        'success': True,
        'count': len(queries),
        'pending_count': pending_count,
        'queries': [q.to_dict() for q in queries]
    }), 200


@admin_bp.route('/api/admin/queries/<int:id>', methods=['PUT'])
@admin_required
@csrf.exempt
def api_update_query(id):
    """Updates admin response and status via REST API."""
    query = StudentQuery.query.get_or_404(id)
    data = request.get_json() or {}

    if 'admin_response' in data:
        query.admin_response = data['admin_response']
    if 'status' in data and data['status'] in StudentQuery.STATUSES:
        query.status = data['status']

    query.updated_at = datetime.now(timezone.utc)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': f"Query #{query.id} updated successfully.",
        'query': query.to_dict()
    }), 200


@admin_bp.route('/api/admin/queries/<int:id>', methods=['DELETE'])
@admin_required
@csrf.exempt
def api_delete_query(id):
    """Deletes query via REST API."""
    query = StudentQuery.query.get_or_404(id)
    db.session.delete(query)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': f"Query #{id} deleted successfully."
    }), 200
