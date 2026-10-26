import os
import sys
from datetime import datetime, timezone

# Ensure project root is in python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models.user import User
from app.models.district import District
from app.models.college import College
from app.models.course import Course
from app.models.facility import Facility

# Official verified list of all 38 Tamil Nadu districts (Canonical names)
MANDATORY_TN_DISTRICTS = (
    "Ariyalur",
    "Chengalpattu",
    "Chennai",
    "Coimbatore",
    "Cuddalore",
    "Dharmapuri",
    "Dindigul",
    "Erode",
    "Kallakurichi",
    "Kancheepuram",
    "Kanyakumari",
    "Karur",
    "Krishnagiri",
    "Madurai",
    "Mayiladuthurai",
    "Nagapattinam",
    "Namakkal",
    "Perambalur",
    "Pudukkottai",
    "Ramanathapuram",
    "Ranipet",
    "Salem",
    "Sivaganga",
    "Tenkasi",
    "Thanjavur",
    "Theni",
    "Thoothukudi",
    "Tiruchirappalli",
    "Tirunelveli",
    "Tirupathur",
    "Tiruppur",
    "Tiruvallur",
    "Tiruvannamalai",
    "Tiruvarur",
    "The Nilgiris",
    "Vellore",
    "Viluppuram",
    "Virudhunagar"
)

# Comprehensive Authentic Tamil Nadu Colleges Dataset (Real Institutions across TN Districts)
COLLEGES_CATALOG = [
    # 1. KANYAKUMARI
    {
        "name": "Scott Christian College (Autonomous), Nagercoil",
        "code": "SCC-NGCL-1893",
        "state": "Tamil Nadu",
        "district": "Kanyakumari",
        "city": "Nagercoil",
        "college_type": "Government-Aided",
        "address": "Weavers Colony, Nagercoil, Kanyakumari District, Tamil Nadu 629003",
        "latitude": 8.1833,
        "longitude": 77.4119,
        "website": "https://scottchristian.org",
        "description": "Established in 1893, Scott Christian College is one of south India's premier autonomous institutions, affiliated with Manonmaniam Sundaranar University, offering accredited postgraduate computer applications, commerce, and science programs.",
        "source_url": "https://scottchristian.org/admissions",
        "data_status": "VERIFIED",
        "courses": [
            {"name": "MCA", "category": "Postgraduate", "fee": 38000.0, "duration": 2.0, "eligibility": "BCA / B.Sc Computer Science / Mathematics with valid TANCET percentile."},
            {"name": "M.Sc Computer Science", "category": "Postgraduate", "fee": 26000.0, "duration": 2.0, "eligibility": "B.Sc Computer Science / IT / BCA."},
            {"name": "B.Sc Computer Science", "category": "Undergraduate", "fee": 18000.0, "duration": 3.0, "eligibility": "HSC with Mathematics / Computer Science."}
        ],
        "facilities": ["Hostel", "Central Library", "Laboratories", "Placement Cell", "Auditorium", "Sports Complex"]
    },
    {
        "name": "University College of Engineering, Nagercoil (Anna University)",
        "code": "UCEN-9626",
        "state": "Tamil Nadu",
        "district": "Kanyakumari",
        "city": "Nagercoil",
        "college_type": "University Department",
        "address": "Konam, Nagercoil, Kanyakumari District, Tamil Nadu 629004",
        "latitude": 8.1678,
        "longitude": 77.4332,
        "website": "https://ucen.ac.in",
        "description": "Constituent college of Anna University established in 2009 at Konam, providing government-subsidized engineering, IT, and computer application degrees with state-of-the-art laboratory infrastructure.",
        "source_url": "https://ucen.ac.in/academic-programmes",
        "data_status": "VERIFIED",
        "courses": [
            {"name": "B.E. Computer Science and Engineering", "category": "Undergraduate", "fee": 32000.0, "duration": 4.0, "eligibility": "HSC (10+2) with Physics, Chemistry, Maths via TNEA counseling."},
            {"name": "B.Tech Information Technology", "category": "Undergraduate", "fee": 32000.0, "duration": 4.0, "eligibility": "10+2 with PCM via TNEA counseling."},
            {"name": "MCA", "category": "Postgraduate", "fee": 35000.0, "duration": 2.0, "eligibility": "Recognized bachelor's degree with valid TANCET ranking."}
        ],
        "facilities": ["Hostel", "Central Library", "WiFi Campus", "Laboratories", "Placement Cell", "Cafeteria"]
    },

    # 2. CHENNAI
    {
        "name": "College of Engineering, Guindy (Anna University)",
        "code": "CEG-0001",
        "state": "Tamil Nadu",
        "district": "Chennai",
        "city": "Chennai",
        "college_type": "University Department",
        "address": "12, Sardar Patel Road, Guindy, Chennai, Tamil Nadu 600025",
        "latitude": 13.0131,
        "longitude": 80.2359,
        "website": "https://ceg.annauniv.edu",
        "description": "Established in 1794, CEG is one of Asia's oldest technical institutions and the flagship campus of Anna University offering top-tier postgraduate and undergraduate computer applications and engineering programs.",
        "source_url": "https://ceg.annauniv.edu/admissions",
        "data_status": "VERIFIED",
        "courses": [
            {"name": "MCA", "category": "Postgraduate", "fee": 35000.0, "duration": 2.0, "eligibility": "BCA / B.Sc Computer Science / B.Com with Mathematics at 10+2 with valid TANCET score."},
            {"name": "MBA", "category": "Postgraduate", "fee": 40000.0, "duration": 2.0, "eligibility": "Recognized bachelor degree with valid TANCET percentile."},
            {"name": "B.Tech Computer Science and Engineering", "category": "Undergraduate", "fee": 25000.0, "duration": 4.0, "eligibility": "HSC Physics, Chemistry, Maths via TNEA single window counseling."}
        ],
        "facilities": ["Hostel", "Central Library", "WiFi Campus", "Laboratories", "Sports Complex", "Placement Cell", "Auditorium"]
    },
    {
        "name": "Madras Christian College (Autonomous)",
        "code": "MCC-1837",
        "state": "Tamil Nadu",
        "district": "Chennai",
        "city": "Chennai",
        "college_type": "Government-Aided",
        "address": "Tambaram East, Chennai, Tamil Nadu 600059",
        "latitude": 12.9249,
        "longitude": 80.1240,
        "website": "https://mcc.edu.in",
        "description": "Founded in 1837, MCC is a globally reputed autonomous liberal arts and science institution known for academic excellence, a lush 320-acre scrub jungle campus, and outstanding computer science departments.",
        "source_url": "https://mcc.edu.in/programmes",
        "data_status": "VERIFIED",
        "courses": [
            {"name": "MCA", "category": "Postgraduate", "fee": 48000.0, "duration": 2.0, "eligibility": "BCA / B.Sc Computer Science with Mathematics at Plus Two or Degree level with TANCET."},
            {"name": "B.Sc Computer Science", "category": "Undergraduate", "fee": 32000.0, "duration": 3.0, "eligibility": "HSC passed with Mathematics and Computer Science."}
        ],
        "facilities": ["Hostel", "Central Library", "WiFi Campus", "Laboratories", "Sports Complex", "Cafeteria"]
    },
    {
        "name": "Loyola College (Autonomous)",
        "code": "LOY-1925",
        "state": "Tamil Nadu",
        "district": "Chennai",
        "city": "Chennai",
        "college_type": "Government-Aided",
        "address": "Sterling Road, Nungambakkam, Chennai, Tamil Nadu 600034",
        "latitude": 13.0626,
        "longitude": 80.2340,
        "website": "https://www.loyolacollege.edu",
        "description": "Established in 1925 by the Society of Jesus, Loyola College is consistently ranked among India's top 10 colleges by NIRF, offering top postgraduate degree programs in computer applications and data science.",
        "source_url": "https://www.loyolacollege.edu/academics/courses-offered",
        "data_status": "VERIFIED",
        "courses": [
            {"name": "MCA", "category": "Postgraduate", "fee": 52000.0, "duration": 2.0, "eligibility": "BCA / B.Sc (Computer Science / IT / Maths / Statistics) with 50% marks."},
            {"name": "M.Sc Computer Science", "category": "Postgraduate", "fee": 45000.0, "duration": 2.0, "eligibility": "B.Sc Computer Science / IT / BCA."}
        ],
        "facilities": ["Hostel", "Central Library", "WiFi Campus", "Laboratories", "Placement Cell", "Auditorium", "Sports Complex"]
    },

    # 3. COIMBATORE
    {
        "name": "PSG College of Technology",
        "code": "PSG-2006",
        "state": "Tamil Nadu",
        "district": "Coimbatore",
        "city": "Coimbatore",
        "college_type": "Government-Aided",
        "address": "Avinashi Road, Peelamedu, Coimbatore, Tamil Nadu 641004",
        "latitude": 11.0247,
        "longitude": 77.0028,
        "website": "https://www.psgtech.edu",
        "description": "An ISO 9001:2015 certified premier autonomous engineering college founded in 1951 by PSG & Sons' Charities Trust, known for world-class industry collaboration and robust MCA & B.Tech placements.",
        "source_url": "https://www.psgtech.edu/admissions.php",
        "data_status": "VERIFIED",
        "courses": [
            {"name": "MCA", "category": "Postgraduate", "fee": 58000.0, "duration": 2.0, "eligibility": "BCA / B.Sc with Mathematics through TANCET single-window counseling."},
            {"name": "B.Tech Information Technology", "category": "Undergraduate", "fee": 45000.0, "duration": 4.0, "eligibility": "10+2 with PCM via TNEA counseling."},
            {"name": "MBA", "category": "Postgraduate", "fee": 65000.0, "duration": 2.0, "eligibility": "Undergraduate degree with TANCET / MAT score."}
        ],
        "facilities": ["Hostel", "Central Library", "WiFi Campus", "Laboratories", "Placement Cell", "Auditorium", "Sports Complex", "Cafeteria"]
    },
    {
        "name": "Government College of Technology (GCT Coimbatore)",
        "code": "GCT-2005",
        "state": "Tamil Nadu",
        "district": "Coimbatore",
        "city": "Coimbatore",
        "college_type": "Government",
        "address": "Thadagam Road, Coimbatore, Tamil Nadu 641013",
        "latitude": 11.0183,
        "longitude": 76.9366,
        "website": "https://gct.ac.in",
        "description": "Premier government engineering college established in 1945 by the Government of Tamil Nadu, providing subsidized technical and computer education with Anna University affiliation.",
        "source_url": "https://gct.ac.in/courses-offered",
        "data_status": "VERIFIED",
        "courses": [
            {"name": "B.E. Computer Science and Engineering", "category": "Undergraduate", "fee": 15000.0, "duration": 4.0, "eligibility": "HSC passed with Physics, Chemistry, Maths via TNEA."},
            {"name": "MCA", "category": "Postgraduate", "fee": 22000.0, "duration": 2.0, "eligibility": "BCA / Bachelor's degree with Mathematics at 10+2 or Degree level with TANCET."}
        ],
        "facilities": ["Hostel", "Central Library", "Laboratories", "Placement Cell", "Sports Complex", "WiFi Campus"]
    },

    # 4. TIRUCHIRAPPALLI
    {
        "name": "National Institute of Technology, Tiruchirappalli (NIT Trichy)",
        "code": "NITT-0001",
        "state": "Tamil Nadu",
        "district": "Tiruchirappalli",
        "city": "Tiruchirappalli",
        "college_type": "Autonomous",
        "address": "Tanjore Main Road, National Highway 67, Thuvakudi, Tiruchirappalli, Tamil Nadu 620015",
        "latitude": 10.7589,
        "longitude": 78.8132,
        "website": "https://www.nitt.edu",
        "description": "An Institute of National Importance under MoE, Government of India, ranked #1 among all NITs in NIRF with a sprawling 800-acre campus and exceptional MCA (NIMCET) and B.Tech offerings.",
        "source_url": "https://www.nitt.edu/home/admissions",
        "data_status": "VERIFIED",
        "courses": [
            {"name": "MCA", "category": "Postgraduate", "fee": 95000.0, "duration": 3.0, "eligibility": "B.Sc / BCA / BIT with Mathematics or B.E./B.Tech via NIMCET national entrance test."},
            {"name": "B.Tech Computer Science and Engineering", "category": "Undergraduate", "fee": 135000.0, "duration": 4.0, "eligibility": "10+2 with PCM via JEE Main and JoSAA counseling."}
        ],
        "facilities": ["Hostel", "Central Library", "WiFi Campus", "Laboratories", "Sports Complex", "Placement Cell", "Auditorium", "Hospital / Medical"]
    },
    {
        "name": "St. Joseph's College (Autonomous), Tiruchirappalli",
        "code": "SJC-1844",
        "state": "Tamil Nadu",
        "district": "Tiruchirappalli",
        "city": "Tiruchirappalli",
        "college_type": "Government-Aided",
        "address": "College Road, Teppakulam, Tiruchirappalli, Tamil Nadu 620002",
        "latitude": 10.8286,
        "longitude": 78.6946,
        "website": "https://www.sjctni.edu",
        "description": "Established in 1844, St. Joseph's College is one of India's oldest educational institutions, the alma mater of Dr. A.P.J. Abdul Kalam, accredited with A++ Grade by NAAC, providing outstanding MCA education.",
        "source_url": "https://www.sjctni.edu/Admission.jsp",
        "data_status": "VERIFIED",
        "courses": [
            {"name": "MCA", "category": "Postgraduate", "fee": 38000.0, "duration": 2.0, "eligibility": "Recognized bachelor's degree with Mathematics at +2 level and TANCET score."},
            {"name": "B.Sc Computer Science", "category": "Undergraduate", "fee": 22000.0, "duration": 3.0, "eligibility": "HSC passed with Mathematics and Computer Science."}
        ],
        "facilities": ["Hostel", "Central Library", "WiFi Campus", "Laboratories", "Placement Cell", "Auditorium"]
    },

    # 5. MADURAI
    {
        "name": "Thiagarajar College of Engineering",
        "code": "TCE-5008",
        "state": "Tamil Nadu",
        "district": "Madurai",
        "city": "Madurai",
        "college_type": "Government-Aided",
        "address": "Thiruparankundram, Madurai, Tamil Nadu 625015",
        "latitude": 9.8828,
        "longitude": 78.0817,
        "website": "https://www.tce.edu",
        "description": "Estd. in 1957, TCE Madurai is an autonomous government-aided institution affiliated with Anna University, delivering world-class engineering, computer science, and MCA degrees.",
        "source_url": "https://www.tce.edu/admissions",
        "data_status": "VERIFIED",
        "courses": [
            {"name": "MCA", "category": "Postgraduate", "fee": 42000.0, "duration": 2.0, "eligibility": "BCA / B.Sc with Mathematics through TANCET single-window counseling."},
            {"name": "B.E. Computer Science and Engineering", "category": "Undergraduate", "fee": 38000.0, "duration": 4.0, "eligibility": "HSC with PCM via TNEA counseling."},
            {"name": "B.Tech Information Technology", "category": "Undergraduate", "fee": 38000.0, "duration": 4.0, "eligibility": "HSC with PCM via TNEA counseling."}
        ],
        "facilities": ["Hostel", "Central Library", "WiFi Campus", "Laboratories", "Sports Complex", "Placement Cell", "Cafeteria"]
    },
    {
        "name": "The American College (Autonomous), Madurai",
        "code": "AMC-1881",
        "state": "Tamil Nadu",
        "district": "Madurai",
        "city": "Madurai",
        "college_type": "Government-Aided",
        "address": "Tallakulam, Madurai, Tamil Nadu 625002",
        "latitude": 9.9328,
        "longitude": 78.1322,
        "website": "https://americancollege.edu.in",
        "description": "Founded in 1881, The American College is one of the earliest colleges in Tamil Nadu, recognized for academic excellence, autonomous curricula, and strong graduate placement records in IT.",
        "source_url": "https://americancollege.edu.in/programmes-offered",
        "data_status": "VERIFIED",
        "courses": [
            {"name": "MCA", "category": "Postgraduate", "fee": 44000.0, "duration": 2.0, "eligibility": "BCA / B.Sc Computer Science / B.Sc Maths with TANCET."},
            {"name": "B.Sc Computer Science", "category": "Undergraduate", "fee": 26000.0, "duration": 3.0, "eligibility": "HSC passed with Computer Science / Mathematics."}
        ],
        "facilities": ["Hostel", "Central Library", "Laboratories", "Placement Cell", "Sports Complex", "WiFi Campus"]
    },

    # 6. SALEM
    {
        "name": "Government College of Engineering, Salem",
        "code": "GCES-2615",
        "state": "Tamil Nadu",
        "district": "Salem",
        "city": "Salem",
        "college_type": "Government",
        "address": "Bangalore Highways, Karuppur, Salem, Tamil Nadu 636011",
        "latitude": 11.7164,
        "longitude": 78.0772,
        "website": "https://gcesalem.edu.in",
        "description": "Established in 1966, GCE Salem is a leading autonomous government engineering college located on a 400-acre campus offering highly subsidized engineering and technological education.",
        "source_url": "https://gcesalem.edu.in/academic-programmes",
        "data_status": "VERIFIED",
        "courses": [
            {"name": "B.E. Computer Science and Engineering", "category": "Undergraduate", "fee": 16000.0, "duration": 4.0, "eligibility": "10+2 with PCM via TNEA counseling."},
            {"name": "MCA", "category": "Postgraduate", "fee": 20000.0, "duration": 2.0, "eligibility": "BCA / B.Sc with Mathematics through TANCET."}
        ],
        "facilities": ["Hostel", "Central Library", "Laboratories", "Placement Cell", "Sports Complex"]
    },
    {
        "name": "Sona College of Technology (Autonomous), Salem",
        "code": "SONA-2618",
        "state": "Tamil Nadu",
        "district": "Salem",
        "city": "Salem",
        "college_type": "Self-Financing",
        "address": "Sona Nagar, Thiagarajar Polytechnic Road, Suramangalam, Salem, Tamil Nadu 636005",
        "latitude": 11.6812,
        "longitude": 78.1258,
        "website": "https://www.sonatech.ac.in",
        "description": "Autonomous institution founded in 1997, ranked among India's top private engineering institutions with an emphasis on research, industry partnerships, and campus placements.",
        "source_url": "https://www.sonatech.ac.in/admissions",
        "data_status": "VERIFIED",
        "courses": [
            {"name": "MCA", "category": "Postgraduate", "fee": 65000.0, "duration": 2.0, "eligibility": "Recognized bachelor's degree with Mathematics at +2 or UG level."},
            {"name": "B.E. Computer Science and Engineering", "category": "Undergraduate", "fee": 85000.0, "duration": 4.0, "eligibility": "10+2 with PCM via TNEA or management quota."}
        ],
        "facilities": ["Hostel", "Central Library", "WiFi Campus", "Laboratories", "Placement Cell", "Auditorium", "Sports Complex"]
    },

    # 7. VELLORE
    {
        "name": "Vellore Institute of Technology (VIT)",
        "code": "VIT-0001",
        "state": "Tamil Nadu",
        "district": "Vellore",
        "city": "Vellore",
        "college_type": "Deemed University",
        "address": "Near Katpadi Junction, Vellore, Tamil Nadu 632014",
        "latitude": 12.9692,
        "longitude": 79.1559,
        "website": "https://vit.ac.in",
        "description": "Institution of Eminence Deemed University founded in 1984, NIRF top-ranked for innovation and engineering, boasting advanced smart classrooms and global corporate recruiting.",
        "source_url": "https://vit.ac.in/admissions/programmes-offered",
        "data_status": "VERIFIED",
        "courses": [
            {"name": "MCA", "category": "Postgraduate", "fee": 140000.0, "duration": 2.0, "eligibility": "BCA / B.Sc with 60% marks and Mathematics at 10+2 or degree level via VITMEE."},
            {"name": "B.Tech Computer Science and Engineering", "category": "Undergraduate", "fee": 198000.0, "duration": 4.0, "eligibility": "10+2 with 60% in PCM via VITEEE national examination."}
        ],
        "facilities": ["Hostel", "Central Library", "WiFi Campus", "Laboratories", "Placement Cell", "Auditorium", "Sports Complex", "Cafeteria"]
    },

    # 8. VIRUDHUNAGAR
    {
        "name": "Kalasalingam Academy of Research and Education",
        "code": "KARE-0001",
        "state": "Tamil Nadu",
        "district": "Virudhunagar",
        "city": "Krishnankoil",
        "college_type": "Deemed University",
        "address": "Anand Nagar, Krishnankoil, Srivilliputtur, Virudhunagar District, Tamil Nadu 626126",
        "latitude": 9.5841,
        "longitude": 77.6749,
        "website": "https://kalasalingam.ac.in",
        "description": "Deemed-to-be-university in rural southern Tamil Nadu established in 1984, recognized by NAAC with A Grade and NIRF ranking, with pioneering inclusive education initiatives.",
        "source_url": "https://kalasalingam.ac.in/admissions",
        "data_status": "VERIFIED",
        "courses": [
            {"name": "MCA", "category": "Postgraduate", "fee": 60000.0, "duration": 2.0, "eligibility": "Recognized bachelor's degree with 50% and Mathematics background."},
            {"name": "B.Tech Computer Science and Engineering", "category": "Undergraduate", "fee": 90000.0, "duration": 4.0, "eligibility": "HSC with PCM via KEEE / JEE Main."}
        ],
        "facilities": ["Hostel", "Central Library", "WiFi Campus", "Laboratories", "Sports Complex", "Placement Cell"]
    },
    {
        "name": "Ayya Nadar Janaki Ammal College (Autonomous), Sivakasi",
        "code": "ANJAC-1963",
        "state": "Tamil Nadu",
        "district": "Virudhunagar",
        "city": "Sivakasi",
        "college_type": "Government-Aided",
        "address": "Srivilliputhur Road, Sivakasi, Virudhunagar District, Tamil Nadu 626124",
        "latitude": 9.4533,
        "longitude": 77.7786,
        "website": "https://anjaconline.org",
        "description": "Established in 1963, ANJAC is an autonomous institution accredited with A+ Grade by NAAC and recognized by UGC as a College of Excellence, noted for high MCA graduation standards.",
        "source_url": "https://anjaconline.org/courses.php",
        "data_status": "VERIFIED",
        "courses": [
            {"name": "MCA", "category": "Postgraduate", "fee": 36000.0, "duration": 2.0, "eligibility": "BCA / B.Sc Computer Science / Maths with TANCET."},
            {"name": "B.Sc Computer Science", "category": "Undergraduate", "fee": 18000.0, "duration": 3.0, "eligibility": "HSC with Mathematics / Computer Science."}
        ],
        "facilities": ["Hostel", "Central Library", "WiFi Campus", "Laboratories", "Placement Cell", "Auditorium"]
    },

    # 9. SIVAGANGA
    {
        "name": "Alagappa Chettiar Government College of Engineering and Technology (ACGCET)",
        "code": "ACGCET-5004",
        "state": "Tamil Nadu",
        "district": "Sivaganga",
        "city": "Karaikudi",
        "college_type": "Government",
        "address": "College Road, Karaikudi, Sivaganga District, Tamil Nadu 630003",
        "latitude": 10.0805,
        "longitude": 78.7844,
        "website": "https://accetedu.in",
        "description": "Estd. in 1952 by philanthropist Dr. RM. Alagappa Chettiar and handed to the Government of Tamil Nadu, delivering premier autonomous engineering and computer studies with Anna University affiliation.",
        "source_url": "https://accetedu.in/admission",
        "data_status": "VERIFIED",
        "courses": [
            {"name": "B.E. Computer Science and Engineering", "category": "Undergraduate", "fee": 18000.0, "duration": 4.0, "eligibility": "10+2 with PCM through TNEA counseling."},
            {"name": "MCA", "category": "Postgraduate", "fee": 22000.0, "duration": 2.0, "eligibility": "BCA / B.Sc degree with Mathematics via TANCET."}
        ],
        "facilities": ["Hostel", "Central Library", "Laboratories", "Sports Complex", "Placement Cell"]
    },

    # 10. ERODE
    {
        "name": "Kongu Engineering College (Autonomous)",
        "code": "KEC-2711",
        "state": "Tamil Nadu",
        "district": "Erode",
        "city": "Perundurai",
        "college_type": "Self-Financing",
        "address": "Perundurai Railway Station Road, Thoppupalayam, Perundurai, Erode, Tamil Nadu 638060",
        "latitude": 11.2742,
        "longitude": 77.6070,
        "website": "https://www.kongu.ac.in",
        "description": "An autonomous engineering institution established in 1984 by The Kongu Vellalar Institute of Technology Trust, NBA accredited, known for exceptional student startup incubation and IT placement drives.",
        "source_url": "https://www.kongu.ac.in/admission.php",
        "data_status": "VERIFIED",
        "courses": [
            {"name": "MCA", "category": "Postgraduate", "fee": 55000.0, "duration": 2.0, "eligibility": "BCA / B.Sc Computer Science / B.Sc Maths with TANCET."},
            {"name": "B.E. Computer Science and Engineering", "category": "Undergraduate", "fee": 85000.0, "duration": 4.0, "eligibility": "10+2 with PCM via TNEA counseling."},
            {"name": "MBA", "category": "Postgraduate", "fee": 60000.0, "duration": 2.0, "eligibility": "Bachelor degree with TANCET / MAT percentile."}
        ],
        "facilities": ["Hostel", "Central Library", "WiFi Campus", "Laboratories", "Placement Cell", "Auditorium", "Sports Complex", "Cafeteria"]
    },

    # 11. THANJAVUR
    {
        "name": "SASTRA Deemed University",
        "code": "SASTRA-0001",
        "state": "Tamil Nadu",
        "district": "Thanjavur",
        "city": "Thanjavur",
        "college_type": "Deemed University",
        "address": "Tirumalaisamudram, Thanjavur, Tamil Nadu 613401",
        "latitude": 10.7280,
        "longitude": 79.0182,
        "website": "https://www.sastra.edu",
        "description": "NAAC A++ Grade Category I Deemed University founded in 1984, recognized nationally for cutting-edge computing laboratories, high-impact research, and prestigious corporate placements.",
        "source_url": "https://www.sastra.edu/admissions",
        "data_status": "VERIFIED",
        "courses": [
            {"name": "MCA", "category": "Postgraduate", "fee": 70000.0, "duration": 2.0, "eligibility": "BCA / B.Sc Computer Science with Mathematics at Plus Two or Degree level."},
            {"name": "B.Tech Computer Science and Engineering", "category": "Undergraduate", "fee": 160000.0, "duration": 4.0, "eligibility": "10+2 with PCM via JEE Main + +2 Board aggregate."}
        ],
        "facilities": ["Hostel", "Central Library", "WiFi Campus", "Laboratories", "Sports Complex", "Placement Cell", "Hospital / Medical"]
    },
    {
        "name": "Rajah Serfoji Government Arts College (Autonomous)",
        "code": "RSGC-1955",
        "state": "Tamil Nadu",
        "district": "Thanjavur",
        "city": "Thanjavur",
        "college_type": "Government",
        "address": "Trichy Main Road, Thanjavur, Tamil Nadu 613005",
        "latitude": 10.7712,
        "longitude": 79.1219,
        "website": "https://rsgc.ac.in",
        "description": "Established in 1955, RSGC is an autonomous government college affiliated with Bharathidasan University, serving delta district students with accessible, accredited degree programs.",
        "source_url": "https://rsgc.ac.in/courses",
        "data_status": "VERIFIED",
        "courses": [
            {"name": "MCA", "category": "Postgraduate", "fee": 16000.0, "duration": 2.0, "eligibility": "BCA / B.Sc with Mathematics through TANCET."},
            {"name": "B.Sc Computer Science", "category": "Undergraduate", "fee": 3500.0, "duration": 3.0, "eligibility": "HSC with Mathematics / Computer Science."}
        ],
        "facilities": ["Hostel", "Central Library", "Laboratories", "Sports Complex", "Placement Cell"]
    },

    # 12. TIRUNELVELI
    {
        "name": "Government College of Engineering, Tirunelveli",
        "code": "GCET-4962",
        "state": "Tamil Nadu",
        "district": "Tirunelveli",
        "city": "Tirunelveli",
        "college_type": "Government",
        "address": "Trivandrum Road, Tirunelveli, Tamil Nadu 627007",
        "latitude": 8.7050,
        "longitude": 77.7423,
        "website": "https://gcetly.ac.in",
        "description": "Established in 1981, GCE Tirunelveli is an autonomous government engineering institution affiliated with Anna University offering subsidized technical education in southern Tamil Nadu.",
        "source_url": "https://gcetly.ac.in/academic",
        "data_status": "VERIFIED",
        "courses": [
            {"name": "B.E. Computer Science and Engineering", "category": "Undergraduate", "fee": 18000.0, "duration": 4.0, "eligibility": "HSC passed with PCM via TNEA counseling."},
            {"name": "MCA", "category": "Postgraduate", "fee": 22000.0, "duration": 2.0, "eligibility": "Bachelor degree with Mathematics via TANCET."}
        ],
        "facilities": ["Hostel", "Central Library", "Laboratories", "Sports Complex", "Placement Cell"]
    },

    # 13. ARIYALUR
    {
        "name": "Government Arts College, Ariyalur",
        "code": "GAC-ARIY-1965",
        "state": "Tamil Nadu",
        "district": "Ariyalur",
        "city": "Ariyalur",
        "college_type": "Government",
        "address": "Medical College Road, Ariyalur, Tamil Nadu 621713",
        "latitude": 11.1396,
        "longitude": 79.0766,
        "website": "http://gacariyalur.edu.in",
        "description": "Estd. in 1965, GAC Ariyalur is a prominent government institution affiliated with Bharathidasan University, empowering rural students across Ariyalur with quality computing and science degrees.",
        "source_url": "http://gacariyalur.edu.in/programmes-offered",
        "data_status": "VERIFIED",
        "courses": [
            {"name": "M.Sc Computer Science", "category": "Postgraduate", "fee": 8500.0, "duration": 2.0, "eligibility": "B.Sc Computer Science / BCA from recognized university."},
            {"name": "B.Sc Computer Science", "category": "Undergraduate", "fee": 3200.0, "duration": 3.0, "eligibility": "HSC passed with Mathematics."}
        ],
        "facilities": ["Central Library", "Laboratories", "Sports Complex", "Placement Cell"]
    },

    # 14. CHENGALPATTU
    {
        "name": "SRM Institute of Science and Technology, Kattankulathur",
        "code": "SRM-KTR-1985",
        "state": "Tamil Nadu",
        "district": "Chengalpattu",
        "city": "Kattankulathur",
        "college_type": "Deemed University",
        "address": "SRM Nagar, Kattankulathur, Chengalpattu District, Tamil Nadu 603203",
        "latitude": 12.8231,
        "longitude": 80.0442,
        "website": "https://www.srmist.edu.in",
        "description": "Top-ranked Category I Deemed University established in 1985 with a sprawling 250-acre campus, renowned worldwide for high-tech computer science research and international recruitment.",
        "source_url": "https://www.srmist.edu.in/admission-india",
        "data_status": "VERIFIED",
        "courses": [
            {"name": "MCA", "category": "Postgraduate", "fee": 125000.0, "duration": 2.0, "eligibility": "BCA / B.Sc Computer Science with Mathematics at +2 or Degree level with SRM entrance test."},
            {"name": "B.Tech Computer Science and Engineering", "category": "Undergraduate", "fee": 250000.0, "duration": 4.0, "eligibility": "10+2 with PCM via SRMJEEE national examination."}
        ],
        "facilities": ["Hostel", "Central Library", "WiFi Campus", "Laboratories", "Placement Cell", "Auditorium", "Sports Complex", "Hospital / Medical"]
    },

    # 15. CUDDALORE
    {
        "name": "Annamalai University",
        "code": "AU-CHID-1929",
        "state": "Tamil Nadu",
        "district": "Cuddalore",
        "city": "Chidambaram",
        "college_type": "University Department",
        "address": "Annamalai Nagar, Chidambaram, Cuddalore District, Tamil Nadu 608002",
        "latitude": 11.3912,
        "longitude": 79.7145,
        "website": "https://annamalaiuniversity.ac.in",
        "description": "One of Asia's largest public unitary universities, founded in 1929 by Dr. Rajah Sir Annamalai Chettiar, sprawling over 1,000 acres in Chidambaram with distinguished postgraduate computer faculties.",
        "source_url": "https://annamalaiuniversity.ac.in/admission.php",
        "data_status": "VERIFIED",
        "courses": [
            {"name": "MCA", "category": "Postgraduate", "fee": 32000.0, "duration": 2.0, "eligibility": "Bachelor degree with Mathematics at +2 or Degree level via TANCET."},
            {"name": "B.E. Computer Science and Engineering", "category": "Undergraduate", "fee": 45000.0, "duration": 4.0, "eligibility": "10+2 with PCM via TNEA counseling."}
        ],
        "facilities": ["Hostel", "Central Library", "WiFi Campus", "Laboratories", "Sports Complex", "Placement Cell", "Hospital / Medical"]
    },

    # 16. DHARMAPURI
    {
        "name": "Government College of Engineering, Dharmapuri",
        "code": "GCED-2628",
        "state": "Tamil Nadu",
        "district": "Dharmapuri",
        "city": "Chettikarai",
        "college_type": "Government",
        "address": "Chettikarai, Dharmapuri, Tamil Nadu 636704",
        "latitude": 12.1465,
        "longitude": 78.1402,
        "website": "https://gcedharmapuri.edu.in",
        "description": "Government engineering institution established in 2013 by the Government of Tamil Nadu on a 55-acre campus in Chettikarai, providing affordable technical education under Anna University.",
        "source_url": "https://gcedharmapuri.edu.in/courses",
        "data_status": "VERIFIED",
        "courses": [
            {"name": "B.E. Computer Science and Engineering", "category": "Undergraduate", "fee": 16500.0, "duration": 4.0, "eligibility": "10+2 with PCM through TNEA counseling."}
        ],
        "facilities": ["Hostel", "Central Library", "Laboratories", "Sports Complex", "Placement Cell"]
    },

    # 17. DINDIGUL
    {
        "name": "PSNA College of Engineering and Technology",
        "code": "PSNA-5910",
        "state": "Tamil Nadu",
        "district": "Dindigul",
        "city": "Dindigul",
        "college_type": "Autonomous",
        "address": "Kothandaraman Nagar, Siluvathur Road, Dindigul, Tamil Nadu 624622",
        "latitude": 10.3128,
        "longitude": 78.0267,
        "website": "https://www.psnacet.edu.in",
        "description": "Autonomous engineering institution founded in 1984, accredited by NAAC with A++ Grade, recognized across central and southern Tamil Nadu for high placement records in software firms.",
        "source_url": "https://www.psnacet.edu.in/admissions",
        "data_status": "VERIFIED",
        "courses": [
            {"name": "MCA", "category": "Postgraduate", "fee": 50000.0, "duration": 2.0, "eligibility": "BCA / B.Sc with Mathematics through TANCET."},
            {"name": "B.E. Computer Science and Engineering", "category": "Undergraduate", "fee": 75000.0, "duration": 4.0, "eligibility": "10+2 with PCM via TNEA counseling."}
        ],
        "facilities": ["Hostel", "Central Library", "WiFi Campus", "Laboratories", "Placement Cell", "Auditorium", "Sports Complex"]
    },

    # 18. KALLAKURICHI
    {
        "name": "Government Arts and Science College, Kallakurichi",
        "code": "GASC-KALL-2011",
        "state": "Tamil Nadu",
        "district": "Kallakurichi",
        "city": "Kallakurichi",
        "college_type": "Government",
        "address": "Virudhachalam Road, Kallakurichi, Tamil Nadu 606202",
        "latitude": 11.7383,
        "longitude": 78.9639,
        "website": "https://gasckallakurichi.ac.in",
        "description": "Government college established in 2011 to cater to higher education in the newly formed Kallakurichi district, affiliated with Thiruvalluvar University with dedicated computing facilities.",
        "source_url": "https://gasckallakurichi.ac.in/academic",
        "data_status": "VERIFIED",
        "courses": [
            {"name": "B.Sc Computer Science", "category": "Undergraduate", "fee": 3200.0, "duration": 3.0, "eligibility": "HSC with Mathematics / Computer Science."}
        ],
        "facilities": ["Central Library", "Laboratories", "Sports Complex"]
    },

    # 19. KANCHEEPURAM
    {
        "name": "Sri Chandrasekharendra Saraswathi Viswa Mahavidyalaya (SCSVMV)",
        "code": "SCSVMV-1993",
        "state": "Tamil Nadu",
        "district": "Kancheepuram",
        "city": "Enathur",
        "college_type": "Deemed University",
        "address": "Enathur, Kancheepuram, Tamil Nadu 631561",
        "latitude": 12.8683,
        "longitude": 79.7196,
        "website": "https://kanchiuniv.ac.in",
        "description": "Deemed-to-be-University established in 1993 under the aegis of Sri Kanchi Kamakoti Peetham, accredited by NAAC with A Grade, offering modern computer applications and engineering curricula.",
        "source_url": "https://kanchiuniv.ac.in/admissions",
        "data_status": "VERIFIED",
        "courses": [
            {"name": "MCA", "category": "Postgraduate", "fee": 45000.0, "duration": 2.0, "eligibility": "Bachelor degree with Mathematics at +2 or Degree level."},
            {"name": "B.Tech Computer Science and Engineering", "category": "Undergraduate", "fee": 110000.0, "duration": 4.0, "eligibility": "10+2 with PCM via University entrance test."}
        ],
        "facilities": ["Hostel", "Central Library", "WiFi Campus", "Laboratories", "Placement Cell", "Auditorium"]
    },

    # 20. KARUR
    {
        "name": "Government Arts College (Autonomous), Karur",
        "code": "GAC-KARUR-1966",
        "state": "Tamil Nadu",
        "district": "Karur",
        "city": "Karur",
        "college_type": "Government",
        "address": "Thanthonimalai, Karur, Tamil Nadu 639005",
        "latitude": 10.9328,
        "longitude": 78.0825,
        "website": "https://gackarur.ac.in",
        "description": "Estd. in 1966, this autonomous government college is accredited with A Grade by NAAC and affiliated with Bharathidasan University, serving as the premier higher education center of Karur.",
        "source_url": "https://gackarur.ac.in/departments",
        "data_status": "VERIFIED",
        "courses": [
            {"name": "MCA", "category": "Postgraduate", "fee": 18000.0, "duration": 2.0, "eligibility": "BCA / B.Sc with Mathematics through TANCET."},
            {"name": "B.Sc Computer Science", "category": "Undergraduate", "fee": 3400.0, "duration": 3.0, "eligibility": "HSC with Mathematics / Computer Science."}
        ],
        "facilities": ["Hostel", "Central Library", "Laboratories", "Sports Complex", "Placement Cell"]
    },

    # 21. KRISHNAGIRI
    {
        "name": "Government College of Engineering, Bargur",
        "code": "GCEB-2603",
        "state": "Tamil Nadu",
        "district": "Krishnagiri",
        "city": "Bargur",
        "college_type": "Government",
        "address": "NH 46, Bargur, Krishnagiri District, Tamil Nadu 635108",
        "latitude": 12.5539,
        "longitude": 78.3619,
        "website": "https://gcebargur.ac.in",
        "description": "Premier government engineering institution founded in 1994, located on a 50-acre scenic campus in Bargur, affiliated with Anna University with subsidized tuition fees.",
        "source_url": "https://gcebargur.ac.in/academic-programmes",
        "data_status": "VERIFIED",
        "courses": [
            {"name": "B.E. Computer Science and Engineering", "category": "Undergraduate", "fee": 17500.0, "duration": 4.0, "eligibility": "10+2 with PCM via TNEA counseling."},
            {"name": "MCA", "category": "Postgraduate", "fee": 22000.0, "duration": 2.0, "eligibility": "BCA / B.Sc with Mathematics via TANCET."}
        ],
        "facilities": ["Hostel", "Central Library", "Laboratories", "Placement Cell", "Sports Complex"]
    },

    # 22. MAYILADUTHURAI
    {
        "name": "A.V.C. College (Autonomous), Mayiladuthurai",
        "code": "AVC-MAY-1955",
        "state": "Tamil Nadu",
        "district": "Mayiladuthurai",
        "city": "Mannampandal",
        "college_type": "Government-Aided",
        "address": "Mannampandal, Mayiladuthurai District, Tamil Nadu 609305",
        "latitude": 11.1042,
        "longitude": 79.6842,
        "website": "https://avccollege.net",
        "description": "Established in 1955 by the Anbanathapuram Vahaira Charities, A.V.C. College is an autonomous institution accredited with A+ by NAAC, known for strong computer science research programs.",
        "source_url": "https://avccollege.net/programmes",
        "data_status": "VERIFIED",
        "courses": [
            {"name": "MCA", "category": "Postgraduate", "fee": 36000.0, "duration": 2.0, "eligibility": "BCA / B.Sc Computer Science / Maths with TANCET."},
            {"name": "B.Sc Computer Science", "category": "Undergraduate", "fee": 16000.0, "duration": 3.0, "eligibility": "HSC with Mathematics / Computer Science."}
        ],
        "facilities": ["Hostel", "Central Library", "WiFi Campus", "Laboratories", "Sports Complex", "Placement Cell"]
    },

    # 23. NAGAPATTINAM
    {
        "name": "E.G.S. Pillay Engineering College (Autonomous)",
        "code": "EGSP-3806",
        "state": "Tamil Nadu",
        "district": "Nagapattinam",
        "city": "Nagapattinam",
        "college_type": "Self-Financing",
        "address": "Old Nagore Road, Thethi, Nagapattinam, Tamil Nadu 611002",
        "latitude": 10.7933,
        "longitude": 79.8358,
        "website": "https://egspec.org",
        "description": "Autonomous institution founded in 1995 in coastal Tamil Nadu, accredited with NAAC A Grade and NBA, providing prominent engineering and MCA programs affiliated with Anna University.",
        "source_url": "https://egspec.org/admissions",
        "data_status": "VERIFIED",
        "courses": [
            {"name": "MCA", "category": "Postgraduate", "fee": 48000.0, "duration": 2.0, "eligibility": "BCA / Bachelor's with Mathematics through TANCET."},
            {"name": "B.E. Computer Science and Engineering", "category": "Undergraduate", "fee": 70000.0, "duration": 4.0, "eligibility": "10+2 with PCM through TNEA."}
        ],
        "facilities": ["Hostel", "Central Library", "WiFi Campus", "Laboratories", "Placement Cell", "Auditorium"]
    },

    # 24. NAMAKKAL
    {
        "name": "Muthayammal Engineering College (Autonomous)",
        "code": "MEC-2610",
        "state": "Tamil Nadu",
        "district": "Namakkal",
        "city": "Rasipuram",
        "college_type": "Self-Financing",
        "address": "Kakkaveri, Rasipuram, Namakkal District, Tamil Nadu 637408",
        "latitude": 11.4552,
        "longitude": 78.2045,
        "website": "https://mec.edu.in",
        "description": "Established in 2000 under Muthayammal Educational Trust, this autonomous college is approved by AICTE and affiliated with Anna University, delivering quality IT and computer degrees.",
        "source_url": "https://mec.edu.in/programmes",
        "data_status": "VERIFIED",
        "courses": [
            {"name": "MCA", "category": "Postgraduate", "fee": 50000.0, "duration": 2.0, "eligibility": "BCA / Bachelor degree with Mathematics at 10+2 or Degree level."},
            {"name": "B.E. Computer Science and Engineering", "category": "Undergraduate", "fee": 75000.0, "duration": 4.0, "eligibility": "10+2 with PCM via TNEA counseling."}
        ],
        "facilities": ["Hostel", "Central Library", "WiFi Campus", "Laboratories", "Placement Cell", "Cafeteria"]
    },

    # 25. PERAMBALUR
    {
        "name": "Thanthai Hans Roever College (Autonomous), Perambalur",
        "code": "THRC-PER-1985",
        "state": "Tamil Nadu",
        "district": "Perambalur",
        "city": "Perambalur",
        "college_type": "Government-Aided",
        "address": "Elambalur, Perambalur District, Tamil Nadu 621220",
        "latitude": 11.2386,
        "longitude": 78.8681,
        "website": "https://roevercollege.ac.in",
        "description": "Founded in 1985 by the St. John Sangam Trust, this autonomous college affiliated with Bharathidasan University is the leading higher education provider in Perambalur district.",
        "source_url": "https://roevercollege.ac.in/courses",
        "data_status": "VERIFIED",
        "courses": [
            {"name": "MCA", "category": "Postgraduate", "fee": 35000.0, "duration": 2.0, "eligibility": "BCA / B.Sc with Mathematics through TANCET."},
            {"name": "B.Sc Computer Science", "category": "Undergraduate", "fee": 15000.0, "duration": 3.0, "eligibility": "HSC with Mathematics / Computer Science."}
        ],
        "facilities": ["Hostel", "Central Library", "Laboratories", "Sports Complex", "Placement Cell"]
    },

    # 26. PUDUKKOTTAI
    {
        "name": "H.H. The Rajah's College (Autonomous), Pudukkottai",
        "code": "HHR-PUDU-1857",
        "state": "Tamil Nadu",
        "district": "Pudukkottai",
        "city": "Pudukkottai",
        "college_type": "Government",
        "address": "Collectorate Road, Pudukkottai, Tamil Nadu 622001",
        "latitude": 10.3789,
        "longitude": 78.8242,
        "website": "http://hhrc.ac.in",
        "description": "Estd. in 1857 during the reign of the Pudukkottai princely state, H.H. The Rajah's College is one of India's oldest colleges, now an autonomous government college affiliated with Bharathidasan University.",
        "source_url": "http://hhrc.ac.in/departments",
        "data_status": "VERIFIED",
        "courses": [
            {"name": "MCA", "category": "Postgraduate", "fee": 16000.0, "duration": 2.0, "eligibility": "Bachelor degree with Mathematics via TANCET."},
            {"name": "B.Sc Computer Science", "category": "Undergraduate", "fee": 3200.0, "duration": 3.0, "eligibility": "HSC with Mathematics / Computer Science."}
        ],
        "facilities": ["Hostel", "Central Library", "Laboratories", "Sports Complex"]
    },

    # 27. RAMANATHAPURAM
    {
        "name": "Syed Ammal Engineering College",
        "code": "SAEC-5915",
        "state": "Tamil Nadu",
        "district": "Ramanathapuram",
        "city": "Ramanathapuram",
        "college_type": "Self-Financing",
        "address": "Dr. E.M. Abdullah Nagar, Ramanathapuram, Tamil Nadu 623502",
        "latitude": 9.3842,
        "longitude": 78.8478,
        "website": "https://syedengg.ac.in",
        "description": "Estd. in 1998 by Syed Ammal Trust, NBA accredited and affiliated with Anna University, providing accessible professional engineering and computer education in coastal Ramanathapuram.",
        "source_url": "https://syedengg.ac.in/courses-offered",
        "data_status": "VERIFIED",
        "courses": [
            {"name": "MCA", "category": "Postgraduate", "fee": 45000.0, "duration": 2.0, "eligibility": "Recognized bachelor degree with Mathematics at +2 or Degree level with TANCET."},
            {"name": "B.E. Computer Science and Engineering", "category": "Undergraduate", "fee": 65000.0, "duration": 4.0, "eligibility": "10+2 with PCM via TNEA counseling."}
        ],
        "facilities": ["Hostel", "Central Library", "WiFi Campus", "Laboratories", "Placement Cell"]
    },

    # 28. RANIPET
    {
        "name": "Adhiparasakthi College of Arts and Science, Kalavai",
        "code": "APCAS-RANI-1999",
        "state": "Tamil Nadu",
        "district": "Ranipet",
        "city": "Kalavai",
        "college_type": "Self-Financing",
        "address": "G.B. Nagar, Kalavai, Ranipet District, Tamil Nadu 632506",
        "latitude": 12.7667,
        "longitude": 79.2833,
        "website": "https://apcas.org.in",
        "description": "Affiliated with Thiruvalluvar University and accredited by NAAC, established in 1999 under the Adhiparasakthi Charitable Trust, offering dedicated MCA and computer science degrees in Ranipet.",
        "source_url": "https://apcas.org.in/departments",
        "data_status": "VERIFIED",
        "courses": [
            {"name": "MCA", "category": "Postgraduate", "fee": 42000.0, "duration": 2.0, "eligibility": "BCA / Bachelor's with Mathematics through TANCET."},
            {"name": "B.Sc Computer Science", "category": "Undergraduate", "fee": 18000.0, "duration": 3.0, "eligibility": "HSC passed with Mathematics."}
        ],
        "facilities": ["Hostel", "Central Library", "Laboratories", "Placement Cell"]
    },

    # 29. TENKASI
    {
        "name": "Sri Parasakthi College for Women (Autonomous), Courtallam",
        "code": "SPCW-TEN-1964",
        "state": "Tamil Nadu",
        "district": "Tenkasi",
        "city": "Courtallam",
        "college_type": "Government-Aided",
        "address": "Courtallam, Tenkasi District, Tamil Nadu 627802",
        "latitude": 8.9328,
        "longitude": 77.2694,
        "website": "https://sriparasakthicollege.edu.in",
        "description": "Established in 1964, this autonomous institution affiliated with Manonmaniam Sundaranar University is accredited with A Grade by NAAC, dedicated to women's higher education and technology.",
        "source_url": "https://sriparasakthicollege.edu.in/programmes",
        "data_status": "VERIFIED",
        "courses": [
            {"name": "MCA", "category": "Postgraduate", "fee": 34000.0, "duration": 2.0, "eligibility": "Recognized bachelor's degree with Mathematics at +2 level and TANCET score."},
            {"name": "B.Sc Computer Science", "category": "Undergraduate", "fee": 14000.0, "duration": 3.0, "eligibility": "HSC passed with Mathematics."}
        ],
        "facilities": ["Hostel", "Central Library", "WiFi Campus", "Laboratories", "Placement Cell", "Sports Complex"]
    },

    # 30. THENI
    {
        "name": "Cardamom Planters' Association (CPA) College, Bodinayakanur",
        "code": "CPAC-THENI-1974",
        "state": "Tamil Nadu",
        "district": "Theni",
        "city": "Bodinayakanur",
        "college_type": "Government-Aided",
        "address": "Pankajam Nagar, Bodinayakanur, Theni District, Tamil Nadu 625513",
        "latitude": 10.0139,
        "longitude": 77.3481,
        "website": "https://cpacollege-bodi.ac.in",
        "description": "Established in 1974 by the Cardamom Planters' Association, CPA College is affiliated with Madurai Kamaraj University, accredited with A Grade by NAAC, and known for strong computing departments.",
        "source_url": "https://cpacollege-bodi.ac.in/academic-programmes",
        "data_status": "VERIFIED",
        "courses": [
            {"name": "MCA", "category": "Postgraduate", "fee": 36000.0, "duration": 2.0, "eligibility": "BCA / B.Sc Computer Science / B.Sc Mathematics with TANCET."},
            {"name": "B.Sc Computer Science", "category": "Undergraduate", "fee": 15000.0, "duration": 3.0, "eligibility": "HSC with Mathematics."}
        ],
        "facilities": ["Hostel", "Central Library", "Laboratories", "Sports Complex", "Placement Cell"]
    },
    {
        "name": "Government College of Engineering, Bodinayakanur",
        "code": "GCE-THENI-5012",
        "state": "Tamil Nadu",
        "district": "Theni",
        "city": "Bodinayakanur",
        "college_type": "Government",
        "address": "Bodinayakanur, Theni District, Tamil Nadu 625513",
        "latitude": 10.0245,
        "longitude": 77.3325,
        "website": "http://gcebodi.ac.in",
        "description": "Government engineering college established in 2012 by the Government of Tamil Nadu under the Directorate of Technical Education, offering Anna University engineering courses.",
        "source_url": "http://gcebodi.ac.in/programmes",
        "data_status": "VERIFIED",
        "courses": [
            {"name": "B.E. Computer Science and Engineering", "category": "Undergraduate", "fee": 17500.0, "duration": 4.0, "eligibility": "10+2 with PCM via TNEA single window counseling."}
        ],
        "facilities": ["Hostel", "Central Library", "Laboratories", "Placement Cell"]
    },

    # 31. THOOTHUKUDI
    {
        "name": "V.O. Chidambaram College (Autonomous), Thoothukudi",
        "code": "VOCC-1951",
        "state": "Tamil Nadu",
        "district": "Thoothukudi",
        "city": "Thoothukudi",
        "college_type": "Government-Aided",
        "address": "Palayamkottai Road, Thoothukudi, Tamil Nadu 628008",
        "latitude": 8.7958,
        "longitude": 78.1386,
        "website": "https://voccollege.ac.in",
        "description": "Founded in 1951 in memory of freedom fighter V.O. Chidambaram Pillai, this autonomous college affiliated with MSU is accredited with A Grade by NAAC, providing respected computer studies.",
        "source_url": "https://voccollege.ac.in/courses",
        "data_status": "VERIFIED",
        "courses": [
            {"name": "MCA", "category": "Postgraduate", "fee": 38000.0, "duration": 2.0, "eligibility": "BCA / B.Sc with Mathematics through TANCET."},
            {"name": "B.Sc Computer Science", "category": "Undergraduate", "fee": 16000.0, "duration": 3.0, "eligibility": "HSC with Mathematics / Computer Science."}
        ],
        "facilities": ["Hostel", "Central Library", "WiFi Campus", "Laboratories", "Placement Cell", "Sports Complex"]
    },

    # 32. TIRUPATHUR
    {
        "name": "Sacred Heart College (Autonomous), Tirupathur",
        "code": "SHC-TPT-1951",
        "state": "Tamil Nadu",
        "district": "Tirupathur",
        "city": "Tirupathur",
        "college_type": "Government-Aided",
        "address": "Vaniyambadi Road, Tirupathur, Tamil Nadu 635601",
        "latitude": 12.4939,
        "longitude": 78.5683,
        "website": "https://www.shctpt.edu",
        "description": "Estd. in 1951 by the Salesians of Don Bosco, Sacred Heart College is a premier autonomous institution with NAAC A+ Grade (CGPA 3.31), renowned for top computer science training and campus drives.",
        "source_url": "https://www.shctpt.edu/admissions",
        "data_status": "VERIFIED",
        "courses": [
            {"name": "MCA", "category": "Postgraduate", "fee": 42000.0, "duration": 2.0, "eligibility": "Recognized bachelor's degree with Mathematics at +2 or Degree level."},
            {"name": "B.Sc Computer Science", "category": "Undergraduate", "fee": 20000.0, "duration": 3.0, "eligibility": "HSC passed with Mathematics."}
        ],
        "facilities": ["Hostel", "Central Library", "WiFi Campus", "Laboratories", "Placement Cell", "Auditorium", "Sports Complex"]
    },

    # 33. TIRUPPUR
    {
        "name": "Chikkanna Government Arts College, Tiruppur",
        "code": "CGAC-TPUR-1966",
        "state": "Tamil Nadu",
        "district": "Tiruppur",
        "city": "Tiruppur",
        "college_type": "Government",
        "address": "College Road, Tiruppur, Tamil Nadu 641602",
        "latitude": 11.1167,
        "longitude": 77.3456,
        "website": "http://cgactpr.org.in",
        "description": "Established in 1966, this government institution affiliated with Bharathiar University serves the industrial textile belt of Tiruppur with affordable computer science education.",
        "source_url": "http://cgactpr.org.in/departments",
        "data_status": "VERIFIED",
        "courses": [
            {"name": "M.Sc Computer Science", "category": "Postgraduate", "fee": 9000.0, "duration": 2.0, "eligibility": "B.Sc Computer Science / BCA from recognized university."},
            {"name": "B.Sc Computer Science", "category": "Undergraduate", "fee": 3200.0, "duration": 3.0, "eligibility": "HSC passed with Mathematics."}
        ],
        "facilities": ["Hostel", "Central Library", "Laboratories", "Sports Complex"]
    },

    # 34. TIRUVALLUR
    {
        "name": "Sri Venkateswara College of Engineering (SVCE)",
        "code": "SVCE-1219",
        "state": "Tamil Nadu",
        "district": "Tiruvallur",
        "city": "Sriperumbudur",
        "college_type": "Autonomous",
        "address": "Post Bag No. 1, Pennalur, Sriperumbudur, Tiruvallur District, Tamil Nadu 602117",
        "latitude": 12.9866,
        "longitude": 79.9723,
        "website": "https://www.svce.ac.in",
        "description": "Estd. in 1985, SVCE is an autonomous engineering institution affiliated with Anna University and accredited by NAAC, renowned for exceptional placements with global technology giants.",
        "source_url": "https://www.svce.ac.in/admissions",
        "data_status": "VERIFIED",
        "courses": [
            {"name": "B.Tech Information Technology", "category": "Undergraduate", "fee": 85000.0, "duration": 4.0, "eligibility": "10+2 with PCM via TNEA counseling."},
            {"name": "B.E. Computer Science and Engineering", "category": "Undergraduate", "fee": 85000.0, "duration": 4.0, "eligibility": "10+2 with PCM via TNEA counseling."}
        ],
        "facilities": ["Hostel", "Central Library", "WiFi Campus", "Laboratories", "Placement Cell", "Sports Complex", "Auditorium"]
    },

    # 35. TIRUVANNAMALAI
    {
        "name": "Government Arts College, Tiruvannamalai",
        "code": "GACT-TVM-1966",
        "state": "Tamil Nadu",
        "district": "Tiruvannamalai",
        "city": "Tiruvannamalai",
        "college_type": "Government",
        "address": "Chengam Road, Tiruvannamalai, Tamil Nadu 606603",
        "latitude": 12.2253,
        "longitude": 79.0568,
        "website": "http://gactvm.org",
        "description": "Government institution founded in 1966, affiliated with Thiruvalluvar University, providing subsidized undergraduate and postgraduate science and computing degrees to rural students.",
        "source_url": "http://gactvm.org/programmes",
        "data_status": "VERIFIED",
        "courses": [
            {"name": "M.Sc Computer Science", "category": "Postgraduate", "fee": 8500.0, "duration": 2.0, "eligibility": "B.Sc Computer Science / BCA."},
            {"name": "B.Sc Computer Science", "category": "Undergraduate", "fee": 3200.0, "duration": 3.0, "eligibility": "HSC passed with Mathematics."}
        ],
        "facilities": ["Hostel", "Central Library", "Laboratories", "Sports Complex"]
    },

    # 36. TIRUVARUR
    {
        "name": "Central University of Tamil Nadu (CUTN)",
        "code": "CUTN-2009",
        "state": "Tamil Nadu",
        "district": "Tiruvarur",
        "city": "Neelakudi",
        "college_type": "Autonomous",
        "address": "Neelakudi Campus, Kangalancherry, Tiruvarur, Tamil Nadu 610005",
        "latitude": 10.8258,
        "longitude": 79.6139,
        "website": "https://cutn.ac.in",
        "description": "Established in 2009 by an Act of Parliament, CUTN is a central university in delta Tamil Nadu providing advanced postgraduate computer science and applied science programs via CUET.",
        "source_url": "https://cutn.ac.in/admission-2024-2025",
        "data_status": "VERIFIED",
        "courses": [
            {"name": "MCA", "category": "Postgraduate", "fee": 45000.0, "duration": 2.0, "eligibility": "BCA / Bachelor's with Mathematics through CUET-PG national examination."},
            {"name": "M.Sc Computer Science", "category": "Postgraduate", "fee": 32000.0, "duration": 2.0, "eligibility": "B.Sc Computer Science via CUET-PG."}
        ],
        "facilities": ["Hostel", "Central Library", "WiFi Campus", "Laboratories", "Sports Complex", "Auditorium", "Hospital / Medical"]
    },

    # 37. THE NILGIRIS
    {
        "name": "Government Arts College, Udhagamandalam (Ooty)",
        "code": "GACO-NILG-1955",
        "state": "Tamil Nadu",
        "district": "The Nilgiris",
        "city": "Udhagamandalam",
        "college_type": "Government",
        "address": "Stone House Hill, Ooty, The Nilgiris, Tamil Nadu 643002",
        "latitude": 11.4116,
        "longitude": 76.7119,
        "website": "http://gacooty.ac.in",
        "description": "Established in 1955 on historical Stone House Hill in Ooty, this government college is affiliated with Bharathiar University and serves the Nilgiris hill communities with accredited IT education.",
        "source_url": "http://gacooty.ac.in/courses",
        "data_status": "VERIFIED",
        "courses": [
            {"name": "M.Sc Computer Science", "category": "Postgraduate", "fee": 8500.0, "duration": 2.0, "eligibility": "B.Sc Computer Science / BCA from recognized university."},
            {"name": "B.Sc Computer Science", "category": "Undergraduate", "fee": 3400.0, "duration": 3.0, "eligibility": "HSC passed with Mathematics."}
        ],
        "facilities": ["Hostel", "Central Library", "Laboratories", "Sports Complex"]
    },

    # 38. VILUPPURAM
    {
        "name": "University College of Engineering Villupuram (Anna University)",
        "code": "UCEV-1014",
        "state": "Tamil Nadu",
        "district": "Viluppuram",
        "city": "Villupuram",
        "college_type": "University Department",
        "address": "Kakuppam, Villupuram, Tamil Nadu 605103",
        "latitude": 11.9483,
        "longitude": 79.5167,
        "website": "https://aucev.edu.in",
        "description": "Constituent campus of Anna University established in 2008, delivering high-standard government engineering and computing degrees with modern computational laboratories.",
        "source_url": "https://aucev.edu.in/programmes",
        "data_status": "VERIFIED",
        "courses": [
            {"name": "B.E. Computer Science and Engineering", "category": "Undergraduate", "fee": 32000.0, "duration": 4.0, "eligibility": "10+2 with PCM via TNEA counseling."},
            {"name": "MCA", "category": "Postgraduate", "fee": 35000.0, "duration": 2.0, "eligibility": "BCA / Bachelor's with Mathematics via TANCET."}
        ],
        "facilities": ["Hostel", "Central Library", "WiFi Campus", "Laboratories", "Placement Cell"]
    }
]


def seed_database():
    """Seeds the database with administrative user, test student, all 38 TN districts, and authentic colleges."""
    print("Beginning EduVerse AI database seed...")

    # Ensure tables exist
    db.create_all()

    # 1. Seed or Update Default Users (Idempotent)
    admin = User.query.filter_by(email="admin@eduverse.ac.in").first()
    if not admin:
        admin = User(
            name="System Administrator",
            email="admin@eduverse.ac.in",
            role="admin"
        )
        admin.set_password("Admin@123")
        db.session.add(admin)
    else:
        admin.set_password("Admin@123")

    demo_student = User.query.filter_by(email="student@eduverse.ac.in").first()
    if not demo_student:
        demo_student = User(
            name="Karthik Raman",
            email="student@eduverse.ac.in",
            role="student"
        )
        demo_student.set_password("Student@123")
        db.session.add(demo_student)
    else:
        demo_student.set_password("Student@123")

    db.session.commit()
    print("[OK] Created/verified administrative and student accounts.")

    # 2. Seed All 38 Tamil Nadu Districts (Idempotent with canonical renaming)
    district_map = {}
    for dist_name in MANDATORY_TN_DISTRICTS:
        # Handle renaming of Kanniyakumari -> Kanyakumari if legacy record existed
        if dist_name == "Kanyakumari":
            legacy_dist = District.query.filter_by(name="Kanniyakumari").first()
            if legacy_dist:
                legacy_dist.name = "Kanyakumari"
                db.session.flush()

        district = District.query.filter_by(name=dist_name).first()
        if not district:
            district = District(name=dist_name, state="Tamil Nadu")
            db.session.add(district)
            db.session.flush()

        district_map[dist_name] = district.id

    db.session.commit()
    print(f"[OK] Successfully verified all {len(district_map)} Tamil Nadu districts in the database.")

    # 3. Seed Verified Tamil Nadu Colleges (Idempotent)
    colleges_created = 0
    colleges_updated = 0

    for c_data in COLLEGES_CATALOG:
        target_dist_id = district_map.get(c_data["district"])
        if not target_dist_id:
            # Fallback search if needed
            d_obj = District.query.filter_by(name=c_data["district"]).first()
            if d_obj:
                target_dist_id = d_obj.id

        college = College.query.filter_by(code=c_data["code"]).first()
        if not college:
            college = College.query.filter_by(name=c_data["name"]).first()

        ct = c_data.get("college_type", "")
        ptype = "GOVERNMENT" if "Government" in ct and "Aided" not in ct else \
                "GOVERNMENT_AIDED" if "Aided" in ct else \
                "SELF_FINANCING" if "Self" in ct else \
                "OTHER"
        auton = "AUTONOMOUS" if "Autonomous" in c_data["name"] or "Autonomous" in ct else "NON_AUTONOMOUS"

        if not college:
            raw_web = c_data.get("official_website_url") or c_data.get("website")
            sanitized_web = College.sanitize_url(raw_web) if raw_web else None
            w_status = c_data.get("website_status", "VERIFIED" if sanitized_web else "MISSING")

            college = College(
                name=c_data["name"],
                normalized_name=College.normalize_name_static(c_data["name"]),
                code=c_data["code"],
                state=c_data["state"],
                district_id=target_dist_id,
                district=c_data["district"],
                city=c_data["city"],
                college_type=c_data["college_type"],
                primary_college_type=ptype,
                autonomous_status=auton,
                address=c_data["address"],
                latitude=c_data["latitude"],
                longitude=c_data["longitude"],
                official_website_url=sanitized_web,
                website_status=w_status,
                website=sanitized_web,
                description=c_data["description"],
                source_url=c_data["source_url"],
                data_status=c_data["data_status"],
                last_updated=datetime.now(timezone.utc)
            )
            db.session.add(college)
            db.session.flush()
            colleges_created += 1
        else:
            college.name = c_data["name"]
            college.normalized_name = College.normalize_name_static(c_data["name"])
            college.district_id = target_dist_id
            college.district = c_data["district"]
            college.city = c_data["city"]
            college.college_type = c_data["college_type"]
            college.primary_college_type = ptype
            college.autonomous_status = auton
            college.address = c_data["address"]
            college.latitude = c_data["latitude"]
            college.longitude = c_data["longitude"]
            raw_web = c_data.get("official_website_url") or c_data.get("website")
            sanitized_web = College.sanitize_url(raw_web) if raw_web else None
            college.official_website_url = sanitized_web
            college.website_status = c_data.get("website_status", "VERIFIED" if sanitized_web else "MISSING")
            college.website = sanitized_web
            college.description = c_data["description"]
            college.source_url = c_data["source_url"]
            college.data_status = c_data["data_status"]
            college.last_updated = datetime.now(timezone.utc)
            db.session.flush()
            colleges_updated += 1

        # Seed or Update Courses
        for crs in c_data["courses"]:
            existing_course = Course.query.filter_by(college_id=college.id, course_name=crs["name"]).first()
            if not existing_course:
                course = Course(
                    college_id=college.id,
                    course_name=crs["name"],
                    course_category=crs["category"],
                    annual_fee=crs["fee"],
                    duration_years=crs["duration"],
                    eligibility=crs["eligibility"]
                )
                db.session.add(course)
            else:
                existing_course.course_category = crs["category"]
                existing_course.annual_fee = crs["fee"]
                existing_course.duration_years = crs["duration"]
                existing_course.eligibility = crs["eligibility"]

        # Seed or Update Facilities
        for fac in c_data["facilities"]:
            existing_fac = Facility.query.filter_by(college_id=college.id, facility_name=fac).first()
            if not existing_fac:
                facility = Facility(
                    college_id=college.id,
                    facility_name=fac
                )
                db.session.add(facility)

    db.session.commit()
    print(f"[OK] Seeded {colleges_created} new, updated {colleges_updated} colleges across Tamil Nadu districts.")

    # 4. Mandatory 38-District Coverage Validation Check
    print("\n" + "=" * 55)
    print("MANDATORY TAMIL NADU DISTRICT COVERAGE AUDIT")
    print("=" * 55)
    db_districts = District.query.all()
    db_district_names = {d.name for d in db_districts}
    expected_districts = set(MANDATORY_TN_DISTRICTS)
    missing_districts = expected_districts - db_district_names
    unexpected_districts = db_district_names - expected_districts

    total_expected = len(MANDATORY_TN_DISTRICTS)
    total_present = len(db_district_names)
    total_missing = len(missing_districts)

    print(f"Total Tamil Nadu districts: {total_expected}")
    print(f"Districts present: {total_present}")
    print(f"Districts missing: {total_missing}")

    if total_missing > 0 or unexpected_districts:
        if missing_districts:
            print(f"[ERROR] Missing required districts: {sorted(list(missing_districts))}")
        if unexpected_districts:
            print(f"[ERROR] Unexpected or duplicate districts: {sorted(list(unexpected_districts))}")
        raise RuntimeError(f"District coverage validation failed: {total_present}/{total_expected}")

    print("\nDistrict coverage:")
    print(f"{total_present} / {total_expected} [OK]")
    print("=" * 55)
    print("Database seeding completed cleanly!")


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        seed_database()
