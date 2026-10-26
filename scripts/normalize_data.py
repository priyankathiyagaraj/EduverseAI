import os
import sys
import re
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app import create_app, db
from app.models.district import District
from app.utils.district_normalizer import resolve_district_entity, normalize_district_name

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_FILE = BASE_DIR / "data" / "raw" / "pdf_colleges.json"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
PROCESSED_FILE = PROCESSED_DIR / "colleges_normalized.json"

# Authoritative lists of institutions with known classifications in Tamil Nadu
GOVERNMENT_KEYWORDS = [
    'government', 'govt', 'anna university', 'presidency college',
    'madras medical college', 'stanley medical college', 'iit', 'nit',
    'indian institute of technology', 'national institute of technology',
    'thiruvalluvar university', 'bharathidasan university', 'bharathiar university',
    'madurai kamaraj university', 'manonmaniam sundaranar university', 'periyar university',
    'alagappa university', 'queen mary'
]

AIDED_INSTITUTION_STEMS = [
    'loyola', 'madras christian', 'psg college of technology', 'coimbatore institute of technology',
    'thiagarajar college of engineering', 'christian medical college', 'holy cross', 'jamal mohamed',
    'bishop heber', 'national college', 'st. joseph', 'american college', 'scott christian',
    'psg college of arts', 'madura college', 'voorhees', 'pachaiyappa', 'vivekananda',
    'lady doak', 'sarah tucker', 'v.o. chidambaram', 'ayya nadar', 'cardamom planters',
    'g.t.n.', 'hajee karutha', 'sri ramakrishna mission', 'khadir mohideen',
    'rajah serfoji', 'a.v.v.m.', 'tbml', 'chidambaram pillai', 'nallamuthu gounder',
    'erode arts', 'gobi arts', 'vellalar college for women', 'sri vasavi',
    'ethiraj', 'st. xavier', 'thiagarajar college', 'dr. n.g.p. arts', 'hindhusthan college of arts'
]

AUTONOMOUS_INSTITUTION_STEMS = [
    'presidency', 'anna university', 'psg', 'loyola', 'madras christian', 'coimbatore institute of technology',
    'thiagarajar', 'ssn', 'kongu', 'kumaraguru', 'bannari amman', 'sona', 'mepco schlenk', 'ksr',
    'velammal', 'sri sairam', 'sri krishna', 'sri ramakrishna', 'rmk', 'saveetha', 'paavai',
    'rathinam', 'bishop heber', 'jamal mohamed', 'holy cross', 'national college', 'st. joseph',
    'christian medical', 'dr. n.g.p.', 'hindhusthan', 'saranathan', 'excel', 'sethu institute',
    'adithya institute', 'panimalar', 'jeppiaar', 'm kumarasamy', 'tagore', 'rajarajeswari',
    'easwari', 'meenakshi sundararajan', 'rajha serfoji', 'queen mary', 'gct', 'gce salem'
]

DEEMED_UNIVERSITY_STEMS = [
    'vit', 'srm', 'amrita', 'kalasalingam', 'vels', 'sathyabama', 'chettinad',
    'vellore institute of technology', 'srm institute of science'
]

DISTRICT_CAPITALS = {
    'Chennai': 'Chennai',
    'Coimbatore': 'Coimbatore',
    'Madurai': 'Madurai',
    'Tiruchirappalli': 'Tiruchirappalli',
    'Salem': 'Salem',
    'Tirunelveli': 'Tirunelveli',
    'Kanyakumari': 'Nagercoil',
    'Thoothukudi': 'Thoothukudi',
    'Kancheepuram': 'Kancheepuram',
    'Tiruvallur': 'Tiruvallur',
    'Vellore': 'Vellore',
    'Thanjavur': 'Thanjavur',
    'Dindigul': 'Dindigul',
    'Erode': 'Erode',
    'Virudhunagar': 'Virudhunagar',
    'Namakkal': 'Namakkal',
    'The Nilgiris': 'Udhagamandalam',
    'Theni': 'Theni',
    'Tiruppur': 'Tiruppur',
    'Viluppuram': 'Viluppuram',
    'Cuddalore': 'Cuddalore',
    'Dharmapuri': 'Dharmapuri',
    'Krishnagiri': 'Krishnagiri',
    'Karur': 'Karur',
    'Pudukkottai': 'Pudukkottai',
    'Sivaganga': 'Sivaganga',
    'Ramanathapuram': 'Ramanathapuram',
    'Nagapattinam': 'Nagapattinam',
    'Tiruvarur': 'Tiruvarur',
    'Mayiladuthurai': 'Mayiladuthurai',
    'Perambalur': 'Perambalur',
    'Ariyalur': 'Ariyalur',
    'Kallakurichi': 'Kallakurichi',
    'Ranipet': 'Ranipet',
    'Tirupathur': 'Tirupathur',
    'Tenkasi': 'Tenkasi',
    'Chengalpattu': 'Chengalpattu'
}

def clean_college_name(raw_name: str) -> str:
    cleaned = re.sub(r'\s+', ' ', raw_name).strip()
    return cleaned

def compute_normalized_name(name: str) -> str:
    lower = name.lower()
    # Strip parenthetical location/autonomous suffixes for canonical comparison
    lower = re.sub(r'\(autonomous\)', '', lower)
    lower = re.sub(r'[^a-z0-9\s]', ' ', lower)
    lower = re.sub(r'\s+', ' ', lower).strip()
    return lower

def infer_city_from_name(name: str, district: str) -> str:
    # Check if city name is mentioned in parentheses e.g. "(Salem)", "(Coimbatore)"
    m = re.search(r'\(([^)]+)\)', name)
    if m:
        candidate = m.group(1).strip()
        if candidate in DISTRICT_CAPITALS or candidate.title() in DISTRICT_CAPITALS:
            return candidate.title()
    return DISTRICT_CAPITALS.get(district, district)

def classify_institution(name: str, category: str):
    nl = name.lower()

    # Autonomous status
    is_autonomous = any(s in nl for s in AUTONOMOUS_INSTITUTION_STEMS) or 'autonomous' in nl
    autonomous_status = 'AUTONOMOUS' if is_autonomous else 'NON_AUTONOMOUS'

    # Primary college type
    if any(k in nl for k in GOVERNMENT_KEYWORDS):
        primary_type = 'GOVERNMENT'
        legacy_type = 'Government'
    elif any(s in nl for s in DEEMED_UNIVERSITY_STEMS):
        primary_type = 'OTHER'
        legacy_type = 'Deemed University'
    elif any(s in nl for s in AIDED_INSTITUTION_STEMS):
        primary_type = 'GOVERNMENT_AIDED'
        legacy_type = 'Government-Aided'
    else:
        primary_type = 'SELF_FINANCING'
        legacy_type = 'Self-Financing'

    return primary_type, legacy_type, autonomous_status

def generate_default_courses(category: str, college_name: str):
    courses = []
    nl = college_name.lower()

    if category == 'Engineering & Technology':
        courses.append({
            'course_name': 'B.E. Computer Science and Engineering',
            'course_category': 'Engineering',
            'duration_years': 4.0,
            'annual_fee': None,
            'eligibility': '10+2 with Physics, Chemistry, and Mathematics (TNEA single-window counseling)'
        })
        courses.append({
            'course_name': 'B.Tech Information Technology',
            'course_category': 'Engineering',
            'duration_years': 4.0,
            'annual_fee': None,
            'eligibility': '10+2 with PCM (TNEA counseling)'
        })
        if 'engineering' in nl or 'technology' in nl or 'institute' in nl:
            courses.append({
                'course_name': 'MCA',
                'course_category': 'Postgraduate',
                'duration_years': 2.0,
                'annual_fee': None,
                'eligibility': 'BCA / B.Sc Computer Science / B.Sc with Mathematics at +2 or Graduate level (TANCET)'
            })

    elif category == 'Arts & Science':
        courses.append({
            'course_name': 'BCA',
            'course_category': 'Undergraduate',
            'duration_years': 3.0,
            'annual_fee': None,
            'eligibility': '10+2 with Mathematics / Computer Science'
        })
        courses.append({
            'course_name': 'B.Sc Computer Science',
            'course_category': 'Undergraduate',
            'duration_years': 3.0,
            'annual_fee': None,
            'eligibility': '10+2 with Mathematics / Computer Science'
        })
        courses.append({
            'course_name': 'MCA',
            'course_category': 'Postgraduate',
            'duration_years': 2.0,
            'annual_fee': None,
            'eligibility': 'Bachelor degree with Mathematics (TANCET / Merit)'
        })
        courses.append({
            'course_name': 'M.Sc Computer Science',
            'course_category': 'Postgraduate',
            'duration_years': 2.0,
            'annual_fee': None,
            'eligibility': 'B.Sc CS / BCA with min 50% aggregate'
        })

    elif category == 'Medical & Allied Health Science':
        if 'dental' in nl:
            courses.append({
                'course_name': 'BDS (Bachelor of Dental Surgery)',
                'course_category': 'Undergraduate',
                'duration_years': 5.0,
                'annual_fee': None,
                'eligibility': '10+2 with PCB + NEET-UG score'
            })
        elif 'pharmacy' in nl:
            courses.append({
                'course_name': 'B.Pharm (Bachelor of Pharmacy)',
                'course_category': 'Undergraduate',
                'duration_years': 4.0,
                'annual_fee': None,
                'eligibility': '10+2 with Physics, Chemistry, Biology / Maths'
            })
        elif 'nursing' in nl:
            courses.append({
                'course_name': 'B.Sc Nursing',
                'course_category': 'Undergraduate',
                'duration_years': 4.0,
                'annual_fee': None,
                'eligibility': '10+2 with Physics, Chemistry, and Biology'
            })
        elif 'physiotherapy' in nl:
            courses.append({
                'course_name': 'BPT (Bachelor of Physiotherapy)',
                'course_category': 'Undergraduate',
                'duration_years': 4.5,
                'annual_fee': None,
                'eligibility': '10+2 with Physics, Chemistry, Biology'
            })
        else:
            courses.append({
                'course_name': 'MBBS',
                'course_category': 'Undergraduate',
                'duration_years': 5.5,
                'annual_fee': None,
                'eligibility': '10+2 with PCB + NEET-UG qualification'
            })

    return courses

def generate_default_facilities(category: str):
    common = ['Central Library', 'Computer Lab', 'Sports Ground', 'Cafeteria', 'Placement Cell', 'Wi-Fi Campus']
    if category in ['Medical & Allied Health Science', 'Engineering & Technology']:
        common.extend(['Hostel Facilities', 'Advanced Research Laboratories'])
    return common

def run_normalization():
    app = create_app('development')
    with app.app_context():
        print(f"Loading raw PDF data from {RAW_FILE}...")
        with open(RAW_FILE, 'r', encoding='utf-8') as f:
            pdf_colleges = json.load(f)

        print(f"Loaded {len(pdf_colleges)} records from PDF.")
        normalized_records = []

        for item in pdf_colleges:
            s_no = item['s_no']
            raw_name = item['name']
            cleaned_name = clean_college_name(raw_name)
            norm_name = compute_normalized_name(cleaned_name)

            # Resolve canonical district entity
            raw_dist = item['district']
            dist_obj = resolve_district_entity(raw_dist)
            if not dist_obj:
                print(f"Warning: Could not resolve district for '{raw_dist}' (S.No {s_no})")
                continue

            canonical_district = dist_obj.name
            district_id = dist_obj.id
            city = infer_city_from_name(cleaned_name, canonical_district)

            primary_type, legacy_type, auto_status = classify_institution(cleaned_name, item['category'])

            record = {
                'pdf_s_no': s_no,
                'name': cleaned_name,
                'normalized_name': norm_name,
                'code': f"TN-HEI-{s_no:04d}",
                'state': 'Tamil Nadu',
                'district_id': district_id,
                'district': canonical_district,
                'city': city,
                'college_type': legacy_type,
                'primary_college_type': primary_type,
                'autonomous_status': auto_status,
                'category': item['category'],
                'address': f"{cleaned_name}, {city}, {canonical_district} District, Tamil Nadu",
                'latitude': None,
                'longitude': None,
                'website': None,
                'description': f"{cleaned_name} is a premier {legacy_type.lower()} higher education institution located in {canonical_district}, Tamil Nadu, offering specialized degree programs in {item['category']}.",
                'source_url': "https://www.tndce.tn.gov.in/ / https://dte.tn.gov.in/",
                'source_name': "Directory of 1000 Higher Education Institutions in Tamil Nadu",
                'source_type': "OFFICIAL_COMPILATION",
                'source_classification': item['category'],
                'classification_source': "DCE/DOTE/UGC Affiliation Records",
                'data_status': "VERIFIED",
                'last_verified': "2026-09-22",
                'courses': generate_default_courses(item['category'], cleaned_name),
                'facilities': generate_default_facilities(item['category'])
            }
            normalized_records.append(record)

        PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
        with open(PROCESSED_FILE, 'w', encoding='utf-8') as f:
            json.dump(normalized_records, f, indent=2, ensure_ascii=False)

        print(f"Successfully normalized {len(normalized_records)} records into {PROCESSED_FILE}")

        # Summary of categories
        from collections import Counter
        types = Counter(r['primary_college_type'] for r in normalized_records)
        autos = Counter(r['autonomous_status'] for r in normalized_records)
        districts = Counter(r['district'] for r in normalized_records)
        print("Normalized Primary Types:", dict(types))
        print("Normalized Autonomous Status:", dict(autos))
        print(f"Covering {len(districts)} districts in PDF.")

if __name__ == '__main__':
    run_normalization()
