from datetime import datetime, timezone
from app import db


class District(db.Model):
    __tablename__ = 'districts'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    state = db.Column(db.String(100), default='Tamil Nadu', nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationship to College
    colleges = db.relationship('College', backref='district_entity', lazy='selectin')

    def to_dict(self, include_counts: bool = False) -> dict:
        data = {
            'id': self.id,
            'name': self.name,
            'state': self.state,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        if include_counts:
            data['college_count'] = len(self.colleges)
        return data

    def __repr__(self) -> str:
        return f"<District {self.id}: {self.name}>"
