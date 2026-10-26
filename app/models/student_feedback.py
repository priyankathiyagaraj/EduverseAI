from datetime import datetime, timezone
import re
from app import db


class StudentFeedback(db.Model):
    """
    Model for storing student ratings and feedback submitted through
    the About Us platform or feedback forms.
    """
    __tablename__ = 'student_feedback'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True)
    student_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=True, index=True)
    rating = db.Column(db.Integer, nullable=False, index=True)  # 1 to 5
    feedback_message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)

    @staticmethod
    def validate_feedback_data(data: dict) -> tuple[bool, str | None]:
        """Validates feedback input payload."""
        if not data:
            return False, "Feedback payload cannot be empty."

        name = (data.get('student_name') or '').strip()
        if not name or len(name) < 2:
            return False, "Please enter your name (at least 2 characters)."
        if len(name) > 100:
            return False, "Name cannot exceed 100 characters."

        email = (data.get('email') or '').strip().lower()
        if email:
            email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
            if not re.match(email_regex, email):
                return False, "Please enter a valid email address."

        try:
            rating = int(data.get('rating', 0))
        except (ValueError, TypeError):
            return False, "Rating must be a valid integer between 1 and 5."

        if rating < 1 or rating > 5:
            return False, "Rating must be between 1 and 5 stars."

        message = (data.get('feedback_message') or '').strip()
        if message and len(message) > 2000:
            return False, "Feedback message must not exceed 2000 characters."

        return True, None

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'student_id': self.student_id,
            'student_name': self.student_name,
            'email': self.email,
            'rating': self.rating,
            'feedback_message': self.feedback_message,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'created_at_date': self.created_at.strftime('%b %d, %Y') if self.created_at else None
        }

    def __repr__(self):
        return f"<StudentFeedback #{self.id} {self.student_name} ({self.rating}★)>"
