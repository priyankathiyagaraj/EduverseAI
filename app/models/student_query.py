from datetime import datetime, timezone
import re
from app import db


class StudentQuery(db.Model):
    """
    Model for student queries submitted through the About Us portal or contact form.
    Stored persistently and managed by administrators.
    """
    __tablename__ = 'student_queries'

    CATEGORIES = (
        'College Information',
        'Course Information',
        'AI Recommendation',
        'Website Issue',
        'Technical Issue',
        'Feedback',
        'Other'
    )

    STATUSES = (
        'PENDING',
        'IN_PROGRESS',
        'RESOLVED',
        'CLOSED'
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True)
    student_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False, index=True)
    phone = db.Column(db.String(25), nullable=True)
    category = db.Column(db.String(50), nullable=False, index=True)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='PENDING', nullable=False, index=True)
    admin_response = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    @staticmethod
    def validate_query_data(data: dict) -> tuple[bool, str | None]:
        """Validates student query submission payload for security and completeness."""
        if not data:
            return False, "Query payload cannot be empty."

        name = (data.get('student_name') or '').strip()
        if not name or len(name) < 2:
            return False, "Please enter your full name (minimum 2 characters)."
        if len(name) > 100:
            return False, "Student name must not exceed 100 characters."

        email = (data.get('email') or '').strip().lower()
        if not email:
            return False, "Email address is required."
        # Email format validation
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(email_regex, email):
            return False, "Please provide a valid email address (e.g., student@example.com)."

        phone = (data.get('phone') or '').strip()
        if phone and not re.match(r'^[+0-9\s\-()]{7,25}$', phone):
            return False, "Phone number format is invalid."

        category = (data.get('category') or '').strip()
        if category not in StudentQuery.CATEGORIES:
            return False, f"Invalid category. Allowed categories: {', '.join(StudentQuery.CATEGORIES)}."

        message = (data.get('message') or '').strip()
        if not message or len(message) < 10:
            return False, "Query message must be at least 10 characters long."
        if len(message) > 3000:
            return False, "Query message must not exceed 3000 characters."

        return True, None

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'student_id': self.student_id,
            'student_name': self.student_name,
            'email': self.email,
            'phone': self.phone,
            'category': self.category,
            'message': self.message,
            'status': self.status,
            'admin_response': self.admin_response,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None,
            'created_at_iso': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f"<StudentQuery #{self.id} {self.student_name} ({self.status})>"
