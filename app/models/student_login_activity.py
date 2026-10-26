from datetime import datetime, timezone
from app import db


class StudentLoginActivity(db.Model):
    """
    Model for tracking student login events and session activity.
    Allows administrators to analyze student engagement, login frequencies,
    and active user trends over time.
    """
    __tablename__ = 'student_login_activity'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    login_time = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    logout_time = db.Column(db.DateTime, nullable=True)
    session_status = db.Column(db.String(20), default='ACTIVE', nullable=False, index=True)  # 'ACTIVE', 'LOGGED_OUT', 'EXPIRED'
    ip_address = db.Column(db.String(45), nullable=True)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'student_id': self.student_id,
            'login_time': self.login_time.strftime('%Y-%m-%d %H:%M:%S') if self.login_time else None,
            'logout_time': self.logout_time.strftime('%Y-%m-%d %H:%M:%S') if self.logout_time else None,
            'session_status': self.session_status,
            'ip_address': self.ip_address
        }

    def __repr__(self):
        return f"<StudentLoginActivity #{self.id} Student #{self.student_id} ({self.session_status})>"
