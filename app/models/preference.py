from datetime import datetime, timezone
import json
from app import db


class StudentPreference(db.Model):
    __tablename__ = 'student_preferences'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True)
    course_name = db.Column(db.String(150), nullable=True)
    state = db.Column(db.String(100), default='Tamil Nadu', nullable=False)
    district = db.Column(db.String(100), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    budget = db.Column(db.Float, nullable=True)
    college_type = db.Column(db.String(100), nullable=True)
    facility_preferences = db.Column(db.Text, nullable=True)  # JSON-encoded array of preferred facilities
    placement_preference = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def get_facilities_list(self) -> list:
        if not self.facility_preferences:
            return []
        try:
            return json.loads(self.facility_preferences)
        except Exception:
            return []

    def set_facilities_list(self, facilities: list) -> None:
        self.facility_preferences = json.dumps(facilities)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'course_name': self.course_name,
            'state': self.state,
            'district': self.district,
            'city': self.city,
            'budget': self.budget,
            'college_type': self.college_type,
            'facilities': self.get_facilities_list(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
