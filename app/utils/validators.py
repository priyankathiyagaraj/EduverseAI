import re
from typing import Tuple, Optional


def validate_email(email: str) -> bool:
    """Checks RFC-compliant email structure."""
    if not email or len(email) > 190:
        return False
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return bool(re.match(email_regex, email.strip()))


def validate_registration_payload(data: dict) -> Tuple[bool, Optional[str]]:
    """Validates user registration input fields."""
    name = data.get('name', '').strip()
    email = data.get('email', '').strip()
    password = data.get('password', '')

    if not name or len(name) < 2:
        return False, "Full name must be at least 2 characters long."
    if len(name) > 100:
        return False, "Full name cannot exceed 100 characters."
    if not validate_email(email):
        return False, "Please enter a valid email address."
    if not password or len(password) < 6:
        return False, "Password must be at least 6 characters long."
    return True, None


def validate_college_payload(data: dict) -> Tuple[bool, Optional[str]]:
    """Validates admin college creation or update payload."""
    name = data.get('name', '').strip()
    district = data.get('district', '').strip()
    city = data.get('city', '').strip()
    college_type = data.get('college_type', '').strip()

    if not name:
        return False, "College name is required."
    if not district:
        return False, "District is required."
    if not city:
        return False, "City is required."
    if not college_type:
        return False, "College type is required."

    lat = data.get('latitude')
    lng = data.get('longitude')
    if lat is not None and lat != '':
        try:
            lat_f = float(lat)
            if not (-90 <= lat_f <= 90):
                return False, "Latitude must be between -90 and 90."
        except ValueError:
            return False, "Latitude must be a valid number."

    if lng is not None and lng != '':
        try:
            lng_f = float(lng)
            if not (-180 <= lng_f <= 180):
                return False, "Longitude must be between -180 and 180."
        except ValueError:
            return False, "Longitude must be a valid number."

    return True, None
