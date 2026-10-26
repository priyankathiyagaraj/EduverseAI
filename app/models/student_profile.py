from datetime import datetime, timezone
import json
from app import db


class StudentProfile(db.Model):
    """
    Persists comprehensive student academic details, 12th stream,
    subject-wise marks, percentage, TNEA cutoff, career interests,
    and personalized guidance history.
    """
    __tablename__ = 'student_profiles'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), unique=True, nullable=True, index=True)
    session_id = db.Column(db.String(100), nullable=True, index=True)

    # Personal Details
    phone = db.Column(db.String(50), nullable=True)
    location = db.Column(db.String(100), nullable=True)
    school = db.Column(db.String(255), nullable=True)

    # 12th Academic Details
    stream = db.Column(db.String(50), nullable=True)  # Science, Commerce, Arts, Vocational / Other
    subject_marks_json = db.Column(db.Text, nullable=True)  # JSON dict of subject -> mark
    total_marks = db.Column(db.Float, nullable=True)
    percentage = db.Column(db.Float, nullable=True)
    tnea_cutoff = db.Column(db.Float, nullable=True)  # Maths/2 + Physics/4 + Chemistry/4

    # Preferences & Interests
    interests_json = db.Column(db.Text, nullable=True)  # JSON list of selected interests
    preferred_course = db.Column(db.String(150), nullable=True)
    preferred_district = db.Column(db.String(100), nullable=True)
    college_preference = db.Column(db.String(100), nullable=True)
    career_interest = db.Column(db.String(150), nullable=True)

    # Cached Assessment Output
    assessment_result_json = db.Column(db.Text, nullable=True)

    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def get_subject_marks(self) -> dict:
        if not self.subject_marks_json:
            return {}
        try:
            return json.loads(self.subject_marks_json)
        except Exception:
            return {}

    def set_subject_marks(self, marks_dict: dict) -> None:
        self.subject_marks_json = json.dumps(marks_dict)

    def get_interests(self) -> list:
        if not self.interests_json:
            return []
        try:
            return json.loads(self.interests_json)
        except Exception:
            return []

    def set_interests(self, interests: list) -> None:
        self.interests_json = json.dumps(interests)

    def get_assessment_result(self) -> dict:
        if not self.assessment_result_json:
            return {}
        try:
            return json.loads(self.assessment_result_json)
        except Exception:
            return {}

    def set_assessment_result(self, result: dict) -> None:
        self.assessment_result_json = json.dumps(result)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'phone': self.phone,
            'location': self.location,
            'school': self.school,
            'stream': self.stream,
            'subject_marks': self.get_subject_marks(),
            'total_marks': self.total_marks,
            'percentage': self.percentage,
            'tnea_cutoff': self.tnea_cutoff,
            'interests': self.get_interests(),
            'preferred_course': self.preferred_course,
            'preferred_district': self.preferred_district,
            'college_preference': self.college_preference,
            'career_interest': self.career_interest,
            'assessment_result': self.get_assessment_result(),
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
