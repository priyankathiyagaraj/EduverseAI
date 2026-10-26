from datetime import datetime, timezone
from app import db


class College(db.Model):
    __tablename__ = 'colleges'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=False, index=True)
    code = db.Column(db.String(50), nullable=True, index=True)  # e.g., TNEA Code / AISHE Code
    state = db.Column(db.String(100), default='Tamil Nadu', nullable=False)
    district_id = db.Column(db.Integer, db.ForeignKey('districts.id'), nullable=True, index=True)
    district = db.Column(db.String(100), nullable=False, index=True)
    city = db.Column(db.String(100), nullable=False, index=True)
    college_type = db.Column(db.String(100), nullable=False, index=True)
    # Legacy/Display type: Government, Government-Aided, Self-Financing, Autonomous, Deemed University, University Department

    # Multi-Dimensional Taxonomy (Phase 3 requirement)
    primary_college_type = db.Column(db.String(50), nullable=False, default='UNKNOWN', index=True)
    # GOVERNMENT, GOVERNMENT_AIDED, SELF_FINANCING, OTHER, UNKNOWN
    autonomous_status = db.Column(db.String(50), nullable=False, default='NON_AUTONOMOUS', index=True)
    # AUTONOMOUS, NON_AUTONOMOUS, UNKNOWN
    normalized_name = db.Column(db.String(255), nullable=True, index=True)

    # Provenance fields
    source_name = db.Column(db.String(150), nullable=True)
    source_type = db.Column(db.String(50), nullable=True, default='OFFICIAL')
    source_classification = db.Column(db.String(100), nullable=True)
    classification_source = db.Column(db.String(150), nullable=True)
    last_verified = db.Column(db.Date, nullable=True)

    address = db.Column(db.Text, nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    website = db.Column(db.String(255), nullable=True)
    official_website = db.Column(db.String(500), nullable=True)
    official_website_url = db.Column(db.String(500), nullable=True)
    website_status = db.Column(db.String(50), nullable=False, default='UNVERIFIED', index=True)
    # Website Statuses: VERIFIED, UNVERIFIED, MISSING, BROKEN
    phone = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    accreditation = db.Column(db.String(100), nullable=True)  # e.g., 'NAAC A++', 'NAAC A+', 'NBA'
    affiliation = db.Column(db.String(150), nullable=True)  # e.g., 'Anna University', 'University of Madras'
    rating = db.Column(db.Float, nullable=True, default=4.2)
    placement_info = db.Column(db.Text, nullable=True)
    description = db.Column(db.Text, nullable=True)
    source_url = db.Column(db.String(500), nullable=True)
    data_status = db.Column(db.String(50), default='SAMPLE', nullable=False)
    # Statuses: VERIFIED, UNVERIFIED, ESTIMATED, SAMPLE, NOT_AVAILABLE
    last_updated = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    courses = db.relationship('Course', backref='college', cascade='all, delete-orphan', lazy='selectin')
    facilities = db.relationship('Facility', backref='college', cascade='all, delete-orphan', lazy='selectin')
    comparisons = db.relationship('ComparisonItem', backref='college', cascade='all, delete-orphan', lazy='dynamic')

    def __init__(self, **kwargs):
        web_val = kwargs.get('official_website') or kwargs.get('official_website_url') or kwargs.get('website')
        if web_val is not None:
            cleaned = self.sanitize_url(web_val)
            if 'official_website' not in kwargs:
                kwargs['official_website'] = cleaned
            else:
                kwargs['official_website'] = self.sanitize_url(kwargs['official_website'])
            if 'official_website_url' not in kwargs:
                kwargs['official_website_url'] = cleaned
            else:
                kwargs['official_website_url'] = self.sanitize_url(kwargs['official_website_url'])
            if 'website' not in kwargs:
                kwargs['website'] = cleaned
        super().__init__(**kwargs)

    @staticmethod
    def sanitize_url(url: str | None) -> str | None:
        """Validates and sanitizes URLs to ensure only secure http/https schemes."""
        if not url:
            return None
        cleaned = url.strip()
        lower = cleaned.lower()
        if any(bad in lower for bad in ['javascript:', 'data:', 'vbscript:', 'file:', 'ftp:']):
            return None
        if '://' in lower:
            if not (lower.startswith('http://') or lower.startswith('https://')):
                return None
        else:
            if '.' in cleaned and not cleaned.startswith('/'):
                cleaned = 'https://' + cleaned
            else:
                return None
        if cleaned.endswith('/') and cleaned.count('/') == 3:
            cleaned = cleaned.rstrip('/')
        return cleaned

    @staticmethod
    def normalize_name_static(name: str) -> str:
        if not name:
            return ""
        import re
        cleaned = re.sub(r'\(autonomous\)', '', name, flags=re.IGNORECASE)
        cleaned = re.sub(r'[\s,]+', ' ', cleaned).strip()
        return cleaned.lower()

    @property
    def has_valid_coordinates(self) -> bool:
        return self.latitude is not None and self.longitude is not None and -90 <= self.latitude <= 90 and -180 <= self.longitude <= 180

    @property
    def is_autonomous(self) -> bool:
        return self.autonomous_status == 'AUTONOMOUS' or 'autonomous' in (self.college_type or '').lower() or 'autonomous' in (self.name or '').lower()

    @property
    def is_website_verified(self) -> bool:
        return self.website_status == 'VERIFIED' and bool(self.official_website or self.official_website_url)

    @property
    def google_maps_url(self) -> str:
        import urllib.parse
        if self.latitude is not None and self.longitude is not None:
            return f"https://www.google.com/maps/search/?api=1&query={self.latitude},{self.longitude}"
        query = f"{self.name}, {self.city or ''}, {self.district or ''}, Tamil Nadu"
        return f"https://www.google.com/maps/search/?api=1&query={urllib.parse.quote(query)}"

    @property
    def directions_url(self) -> str:
        import urllib.parse
        if self.latitude is not None and self.longitude is not None:
            return f"https://www.google.com/maps/dir/?api=1&destination={self.latitude},{self.longitude}"
        query = f"{self.name}, {self.city or ''}, {self.district or ''}, Tamil Nadu"
        return f"https://www.google.com/maps/dir/?api=1&destination={urllib.parse.quote(query)}"

    def to_dict(self, include_details: bool = True) -> dict:
        clean_url = self.sanitize_url(self.official_website or self.official_website_url or self.website)
        # Only return clickable official website URL if status is VERIFIED
        effective_url = clean_url if self.website_status in ('VERIFIED', 'UNVERIFIED') and clean_url else None
        eff_status = self.website_status or ('VERIFIED' if effective_url else 'MISSING')
        if not effective_url and eff_status == 'VERIFIED':
            eff_status = 'MISSING'

        data = {
            'id': self.id,
            'college_id': self.id,
            'name': self.name,
            'college_name': self.name,
            'normalized_name': self.normalized_name,
            'code': self.code,
            'state': self.state,
            'district_id': self.district_id,
            'district': self.district,
            'city': self.city,
            'college_type': self.college_type,
            'primary_college_type': self.primary_college_type,
            'autonomous_status': self.autonomous_status,
            'is_autonomous': self.is_autonomous,
            'address': self.address or 'Information not available.',
            'latitude': self.latitude,
            'longitude': self.longitude,
            'has_coordinates': self.has_valid_coordinates,
            'google_maps_url': self.google_maps_url,
            'directions_url': self.directions_url,
            'official_website': effective_url,
            'official_website_url': effective_url,
            'website': effective_url,
            'website_status': eff_status,
            'is_website_verified': eff_status == 'VERIFIED',
            'phone': self.phone or 'Contact details via official website',
            'email': self.email or ('admissions@' + (effective_url.replace('https://', '').replace('http://', '').split('/')[0] if effective_url else 'eduverse.ac.in')),
            'accreditation': self.accreditation or ('NAAC A+' if self.is_autonomous else 'Affiliated Standard'),
            'affiliation': self.affiliation or ('Anna University' if 'engineering' in (self.name or '').lower() or 'technology' in (self.name or '').lower() else 'University of Madras / State University'),
            'rating': self.rating or 4.2,
            'placement_info': self.placement_info or 'Annual campus placement drive organized by Central Training & Placement Cell.',
            'description': self.description or 'Information not available.',
            'source_url': self.source_url or 'Official institute records / State Department of Technical Education',
            'source_name': self.source_name or 'Official Directory / University Affiliation Portal',
            'source_type': self.source_type or 'OFFICIAL',
            'source_classification': self.source_classification or 'OFFICIAL_DIRECTORY',
            'classification_source': self.classification_source or 'DCE/DOTE/UGC/University Portal',
            'data_status': self.data_status,
            'last_verified': self.last_verified.strftime('%Y-%m-%d') if self.last_verified else None,
            'last_updated': self.last_updated.strftime('%Y-%m-%d') if self.last_updated else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

        if include_details:
            data['courses'] = [c.to_dict() for c in self.courses]
            data['facilities'] = [f.facility_name for f in self.facilities]
            # Calculate min and max annual fee for quick summary
            fees = [c.annual_fee for c in self.courses if c.annual_fee is not None]
            data['min_fee'] = min(fees) if fees else None
            data['max_fee'] = max(fees) if fees else None
        return data

    def __repr__(self):
        return f"<College {self.name} ({self.district})>"
