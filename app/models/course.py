from datetime import datetime, timezone
from app import db


class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    college_id = db.Column(db.Integer, db.ForeignKey('colleges.id', ondelete='CASCADE'), nullable=False, index=True)
    course_name = db.Column(db.String(150), nullable=False, index=True)
    course_category = db.Column(db.String(100), nullable=True, index=True)  # e.g., 'Postgraduate', 'Undergraduate', 'Engineering', 'Management'
    degree = db.Column(db.String(50), nullable=True, index=True)  # e.g., 'PG', 'UG', 'Diploma', 'Doctoral'
    department = db.Column(db.String(120), nullable=True)  # e.g., 'Computer Applications', 'Computer Science & Engineering', 'Management Studies'
    annual_fee = db.Column(db.Float, nullable=True)  # Strictly None if unavailable, never 0
    duration_years = db.Column(db.Float, nullable=True)  # e.g., 2.0, 3.0, 4.0
    intake_seats = db.Column(db.Integer, nullable=True)  # e.g., 60, 120, 180
    admission_mode = db.Column(db.String(120), nullable=True)  # e.g., 'TANCET Single-Window Counseling', 'TNEA Counseling', 'Merit'
    eligibility = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'college_id': self.college_id,
            'course_name': self.course_name,
            'course_category': self.course_category,
            'degree': self.degree,
            'department': self.department,
            'annual_fee': self.annual_fee,
            'duration_years': self.duration_years,
            'intake_seats': self.intake_seats,
            'admission_mode': self.admission_mode or 'TANCET / TNEA / State Directorate Norms',
            'eligibility': self.eligibility or 'As prescribed by Anna University / Directorate of Technical Education norms.',
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f"<Course {self.course_name} (College {self.college_id})>"
