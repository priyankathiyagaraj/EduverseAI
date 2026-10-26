import os
import sys

# Ensure project root is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models.district import District
from app.models.college import College
from app.models.course import Course
from app.models.facility import Facility


def validate_data_coverage():
    """Generates the required EduVerse Data Coverage report."""
    districts = District.query.order_by(District.name.asc()).all()
    total_districts = len(districts)

    colleges = College.query.all()
    total_colleges = len(colleges)
    total_courses = Course.query.count()
    total_facilities = Facility.query.count()

    districts_with_colleges = []
    districts_without_colleges = []

    for d in districts:
        c_count = len(d.colleges)
        if c_count > 0:
            districts_with_colleges.append((d.name, c_count))
        else:
            districts_without_colleges.append(d.name)

    print("--------------------------------")
    print("EDUVERSE DATA COVERAGE")
    print("--------------------------------")
    print(f"Total districts:\n{total_districts}\n")
    print(f"Districts with college records:\n{len(districts_with_colleges)}\n")
    print(f"Districts without college records:\n{len(districts_without_colleges)}\n")
    print(f"Total college records:\n{total_colleges}\n")
    print(f"Total course records:\n{total_courses}\n")
    print(f"Total facility records:\n{total_facilities}")
    print("--------------------------------\n")

    if districts_without_colleges:
        print("Districts without college records:")
        for idx, name in enumerate(districts_without_colleges, 1):
            print(f"{idx}. {name}")
    else:
        print("All 38 districts currently contain verified college records!")

    # Check specifically for Kanyakumari
    kanya = District.query.filter(District.name.in_(['Kanyakumari', 'Kanniyakumari'])).first()
    if kanya:
        k_count = len(kanya.colleges)
        print(f"\n[AUDIT] Kanyakumari college records: {k_count}")
    else:
        print("\n[WARNING] Kanyakumari district not found in districts table!")

    return {
        'total_districts': total_districts,
        'districts_with_colleges': len(districts_with_colleges),
        'districts_without_colleges': len(districts_without_colleges),
        'total_colleges': total_colleges,
        'total_courses': total_courses,
        'total_facilities': total_facilities
    }


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        validate_data_coverage()
