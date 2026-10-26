from datetime import datetime, timezone
from app import db


class DatasetMetadata(db.Model):
    __tablename__ = 'dataset_metadata'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    dataset_version = db.Column(db.String(50), nullable=False)
    source = db.Column(db.String(255), nullable=False)
    retrieved_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    total_records = db.Column(db.Integer, nullable=False, default=0)
    verified_records = db.Column(db.Integer, nullable=False, default=0)
    notes = db.Column(db.Text, nullable=True)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'dataset_version': self.dataset_version,
            'source': self.source,
            'retrieved_at': self.retrieved_at.isoformat() if self.retrieved_at else None,
            'total_records': self.total_records,
            'verified_records': self.verified_records,
            'notes': self.notes
        }

    def __repr__(self):
        return f"<DatasetMetadata v{self.dataset_version}: {self.total_records} records>"
