from datetime import datetime, timezone
from app import db


class ComparisonItem(db.Model):
    __tablename__ = 'comparison_items'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    session_key = db.Column(db.String(100), nullable=True, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=True, index=True)
    college_id = db.Column(db.Integer, db.ForeignKey('colleges.id', ondelete='CASCADE'), nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'session_key': self.session_key,
            'user_id': self.user_id,
            'college_id': self.college_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f"<ComparisonItem College:{self.college_id} User:{self.user_id} Session:{self.session_key}>"
