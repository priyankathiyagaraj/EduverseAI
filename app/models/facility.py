from app import db


class Facility(db.Model):
    __tablename__ = 'facilities'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    college_id = db.Column(db.Integer, db.ForeignKey('colleges.id', ondelete='CASCADE'), nullable=False, index=True)
    facility_name = db.Column(db.String(100), nullable=False, index=True)

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'college_id': self.college_id,
            'facility_name': self.facility_name
        }

    def __repr__(self):
        return f"<Facility {self.facility_name} (College {self.college_id})>"
