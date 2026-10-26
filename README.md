# EduVerse AI
## Smart College Recommendation System for Tamil Nadu

[![Python 3.12](https://img.shields.io/badge/Python-3.12-blue.svg)](https://www.python.org/)
[![Flask 3.1](https://img.shields.io/badge/Flask-3.1-black.svg)](https://flask.palletsprojects.com/)
[![SQLAlchemy 2.0](https://img.shields.io/badge/SQLAlchemy-2.0-red.svg)](https://www.sqlalchemy.org/)
[![MySQL Compatible](https://img.shields.io/badge/Database-MySQL%20%2F%20SQLite-orange.svg)](https://www.mysql.com/)
[![Pytest Passed](https://img.shields.io/badge/Tests-47%20Passed-brightgreen.svg)](https://pytest.org/)
[![Colleges](https://img.shields.io/badge/Colleges-1%2C129%20Cataloged-blueviolet.svg)](https://github.com/)
[![Districts Covered](https://img.shields.io/badge/Districts-38%20%2F%2038%20(100%25)-success.svg)](https://github.com/)
[![Scikit-Learn](https://img.shields.io/badge/ML-Scikit--Learn%20CBF-yellowgreen.svg)](https://scikit-learn.org/)

An MCA Final-Year Project and production-grade web application designed to help students, parents, and academic counselors discover, search, compare, and receive explainable recommendations for colleges and degree programs across Tamil Nadu, India.

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [Problem Statement](#problem-statement)
3. [Objectives](#objectives)
4. [Features](#features)
5. [System Architecture](#system-architecture)
6. [Technology Stack](#technology-stack)
7. [Database Schema](#database-schema)
8. [Installation & Setup](#installation--setup)
   - [Virtual Environment Setup](#virtual-environment-setup)
   - [MySQL Database Setup](#mysql-database-setup)
   - [Environment Configuration (.env)](#environment-configuration-env)
   - [Database Migrations (Flask-Migrate)](#database-migrations-flask-migrate)
   - [Database Seeding](#database-seeding)
   - [Running the Application](#running-the-application)
9. [ML Workflow & Recommendation Algorithm](#ml-workflow--recommendation-algorithm)
10. [REST API Documentation](#rest-api-documentation)
11. [Testing & Quality Assurance](#testing--quality-assurance)
12. [Data Quality & Transparency Model](#data-quality--transparency-model)
13. [Security Architecture](#security-architecture)
14. [Known Limitations](#known-limitations)
15. [Future Enhancements Roadmap](#future-enhancements-roadmap)
16. [Project Structure](#project-structure)
17. [Academic Viva Explanation Guide](#academic-viva-explanation-guide)
18. [Author & Project Information](#author--project-information)

---

## Project Overview

**EduVerse AI** is a full-stack educational decision-support platform tailored for Tamil Nadu higher education. The platform brings structured transparency to admission discovery by aggregating colleges across districts (Chennai, Coimbatore, Madurai, Tiruchirappalli, Salem, etc.), modeling their fee structures and campus amenities, and providing an explainable, multi-criteria recommendation engine powered by content-based filtering.

---

## Problem Statement

Every academic year, students graduating from higher secondary (10+2) or undergraduate programs (such as BCA or B.Sc) in Tamil Nadu face major systemic obstacles:
1. **Scattered College Information**: Key data regarding tuition fees, sanctioned programs, and hostel facilities are dispersed across dozens of unstandardized college websites and state university gazettes.
2. **Difficult Manual Comparison**: Students often maintain ad-hoc spreadsheets or hand-written notes to evaluate options, making it hard to see direct trade-offs.
3. **Limited Personalization**: Traditional portals only offer blunt binary keyword searches, failing to match student budgets, location constraints, and desired facilities simultaneously.
4. **Opaque Claims & Bias**: Commercial education portals frequently invent subjective rankings, promote sponsored colleges as "Rank #1", or fabricate unverified placement percentages.

---

## Objectives

- Build a normalized, relational database of Tamil Nadu institutions, courses, annual fees, and amenities.
- Provide a multi-parametric search engine allowing simultaneous filtering across programs (MCA, MBA, B.Tech), districts, college types, fees, and facilities.
- Deliver an objective, side-by-side comparison matrix comparing 2 to 4 colleges without arbitrary winner declarations.
- Implement an explainable Content-Based Recommendation algorithm scoring institutions based on explicit preference vectors and providing human-readable match factors.
- Create real-time analytics visualizations using Chart.js powered strictly by live database records.
- Implement a geographic campus explorer using Leaflet.js and OpenStreetMap with strict GPS coordinate verification.
- Provide role-based administration (Student vs. Administrator) with secure server-side access controls.

---

## Features

### 1. Multi-Parametric College Explorer (`/explore`)
- Search by college name, degree program (MCA, MBA, B.Tech, BCA), district, or city.
- Filter by institution type: Government, Government-Aided, Autonomous, Self-Financing, Deemed University, or University Department.
- Annual tuition budget ceiling slider (₹15,000 to ₹2,50,000+).
- Campus amenity multi-selection (Hostel, Central Library, WiFi Campus, Placement Cell, Sports Complex, etc.).
- Server-side pagination with dynamic URL query parameters.
- Toggleable Leaflet map view plotting filtered campuses geographically.

### 2. Side-by-Side Comparison Matrix (`/compare`)
- Compare between 2 and 4 institutions concurrently.
- Enforces duplicate prevention and maximum 4 college constraints.
- Factual attribute comparison: Location, Data Status, Annual Fee Range, Cataloged Courses, Amenities, and Official Source URLs.
- Missing values explicitly labeled as *"Information not available"* instead of zero or false.

### 3. Explainable AI Recommender (`/recommendations`)
- Content-based multi-criteria scoring algorithm.
- Mathematically bounded scores (0.0% to 100.0% match).
- Human-readable diagnostic breakdown of matching factors (e.g. *✓ MCA course offered*, *✓ Within budget of ₹1,00,000*, *✓ Located in preferred district*).
- Ethical disclaimer prominently displayed: *"Recommendations are informational and depend on the quality and freshness of available data."*

### 4. Real-Time Analytics Dashboard (`/analytics`)
- 4 interactive Chart.js visualizations driven by live database queries:
  1. Colleges by District (regional coverage distribution)
  2. College Distribution by Type (governance split)
  3. Annual Tuition Fee Brackets (affordability spread)
  4. Top Program Availability (course frequency)
- Live database KPI counters for institutions indexed, degree programs cataloged, and verification audit counts.

### 5. Campus Location Map (`/map`)
- Leaflet.js with OpenStreetMap standard tiles and attribution.
- Validates latitude and longitude before plotting. Institutions without verified coordinates display *"Location coordinates unavailable"* rather than plotting bogus coordinates.

### 6. Authentication & Role-Based Access Control
- Student and Administrator user roles.
- Passwords hashed using Werkzeug PBKDF2-HMAC-SHA256.
- Role-based server-side guard `@admin_required`. Unauthorized users receive HTTP 403 Forbidden.

### 7. Admin Management Console (`/admin`)
- Comprehensive CRUD: Add, edit, and delete colleges.
- Manage degree courses, duration, and tuition fee schedules.
- Update campus facilities and verification statuses (`VERIFIED`, `SAMPLE`, `ESTIMATED`, `NOT_AVAILABLE`).
- Update source audit URLs and timestamps.

---

## System Architecture

```
[ Web Browser / Client ]
  - HTML5, Tailwind CSS, Vanilla JavaScript
  - Leaflet.js & OpenStreetMap
  - Chart.js Visualizations
         │
         │  HTTP / REST / JSON
         ▼
[ Flask Application Core ]
  - Application Factory: create_app()
  - Blueprints: main, auth, colleges, comparison, recommendations, analytics, admin
  - Security: Flask-WTF (CSRF), Werkzeug Password Hashing, Session Guards
         │
  ┌──────┴───────────────────────────┐
  ▼                                  ▼
[ Service Layer ]          [ Recommendation Engine ]
  - CollegeService           - CollegeFeatureExtractor (scikit-learn)
  - ComparisonService        - RecommendationScorer (Multi-Criteria Weighted Model)
  - AnalyticsService         - ContentBasedRecommender
  - ValidationService        - Explainable Match Factor Generator
  ┌──────────────────────────────────┘
  ▼
[ SQLAlchemy 2.0 ORM ]
  │
  ├─► [ MySQL Database ]           (Production / Academic Viva Demo)
  └─► [ SQLite In-Memory Database ] (Automated Pytest Suite / Offline Dev)
```

---

## Technology Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Frontend UI** | HTML5, Tailwind CSS, Jinja2 | Responsive, clean, academic presentation |
| **Frontend Logic** | Vanilla JavaScript (ES6+) | Dynamic fetch calls, DOM updates, compare state |
| **Mapping** | Leaflet.js, OpenStreetMap | Campus geolocation plotting with popups |
| **Analytics Charts** | Chart.js 4.4 | Real-time database distribution charts |
| **Backend Web** | Python 3.12, Flask 3.1 | Application server & Blueprint routing |
| **Database ORM** | SQLAlchemy 2.0, Flask-SQLAlchemy | Object-relational mapping, parameterized queries |
| **Migrations** | Flask-Migrate 4.1, Alembic | Version-controlled database schema migrations |
| **Database Engines** | MySQL 8.0 / SQLite 3 | Normalized relational persistence |
| **Database Driver** | PyMySQL 1.1, Cryptography | Native Python MySQL connection driver |
| **Machine Learning** | Pandas 2.2, NumPy 2.2, Scikit-Learn 1.6 | Feature vectorization, multi-label binarizing, scoring |
| **Testing** | Pytest 8.3 | Automated unit and integration testing suite |

---

## Database Schema

Normalized relational design with cascading integrity constraints:

```mermaid
erDiagram
    users ||--o{ student_preferences : "saves"
    users ||--o{ comparison_items : "adds"
    districts ||--o{ colleges : "contains (FK)"
    colleges ||--o{ courses : "offers (CASCADE)"
    colleges ||--o{ facilities : "provides (CASCADE)"
    colleges ||--o{ comparison_items : "referenced in (CASCADE)"

    districts {
        int id PK
        string name UK "38 Official Districts"
        string state "Tamil Nadu"
        datetime created_at
    }

    users {
        int id PK
        string name
        string email UK
        string password_hash
        string role "student | admin"
        datetime created_at
    }

    colleges {
        int id PK
        int district_id FK
        string name
        string code "TNEA/AISHE"
        string state "Tamil Nadu"
        string district
        string city
        string college_type
        text address
        float latitude
        float longitude
        string website
        text description
        string source_url
        string data_status "VERIFIED | SAMPLE | ESTIMATED | NOT_AVAILABLE"
        datetime last_updated
        datetime created_at
    }

    courses {
        int id PK
        int college_id FK
        string course_name
        string course_category
        float annual_fee "NULL if unknown"
        float duration_years
        text eligibility
        datetime created_at
    }

    facilities {
        int id PK
        int college_id FK
        string facility_name
    }

    student_preferences {
        int id PK
        int user_id FK
        string course_name
        string district
        string city
        float budget
        string college_type
        text facility_preferences
        datetime created_at
    }

    comparison_items {
        int id PK
        string session_key
        int user_id FK
        int college_id FK
        datetime created_at
    }
```

---

## Installation & Setup

### Prerequisites
- Python 3.12+ (Verify with `python --version`)
- MySQL 8.0+ (Optional: SQLite fallback is active by default for immediate execution)
- Git

### 1. Virtual Environment Setup

Clone the repository and initialize the Python virtual environment:

```bash
# Clone the repository
git clone https://github.com/your-username/eduverse-ai.git
cd eduverse-ai

# Create virtual environment
python -m venv venv

# Activate virtual environment (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Activate virtual environment (Linux / macOS)
source venv/bin/activate

# Upgrade pip and install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### 2. MySQL Database Setup

1. Open your MySQL client (MySQL Workbench, phpMyAdmin, or terminal):
```sql
CREATE DATABASE eduverse_ai CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2. Create a dedicated database user or use `root`:
```sql
CREATE USER 'eduverse_user'@'localhost' IDENTIFIED BY 'eduverse_password';
GRANT ALL PRIVILEGES ON eduverse_ai.* TO 'eduverse_user'@'localhost';
FLUSH PRIVILEGES;
```

### 3. Environment Configuration (`.env`)

Copy the provided `.env.example` to `.env`:

```bash
cp .env.example .env
```

Configure your `.env` variables:

```ini
FLASK_APP=run.py
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=your_secure_random_session_key_here

# MySQL Configuration
MYSQL_USER=eduverse_user
MYSQL_PASSWORD=eduverse_password
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=eduverse_ai

# Explicit Database URI:
# For MySQL:
DATABASE_URL=mysql+pymysql://eduverse_user:eduverse_password@localhost:3306/eduverse_ai
# Or for local SQLite:
# DATABASE_URL=sqlite:///eduverse_dev.db
```

### 4. Database Migrations (Flask-Migrate)

Initialize and apply database schema migrations:

```bash
# Initialize database tables using migrations
flask db upgrade
```

To create new migrations after model changes:
```bash
flask db migrate -m "Description of schema changes"
flask db upgrade
```

### 5. Database Seeding & Dataset Ingestion Pipeline

EduVerse AI features an idempotent, multi-stage ingestion pipeline to process and audit institutions from official government directories and university registers:

```bash
# Seed default administrative and student accounts + baseline catalog
python seed/seed_data.py

# Ingest and validate the comprehensive Tamil Nadu dataset (1,129 colleges):
# 1. Parse raw directory institutions
python scripts/collect_data.py

# 2. Normalize districts, names, degree programs, and taxonomy
python scripts/normalize_data.py

# 3. Deduplicate against state university registers
python scripts/deduplicate_data.py

# 4. Import cleanly into database (100% idempotent)
python scripts/import_data.py

# 5. Execute live validation audit suite
python scripts/validate_data.py
```

#### Production Dataset Audit Metrics

| Metric / Dimension | Target Threshold | Actual Verified in EduVerse AI | Status |
|:---|:---:|:---:|:---:|
| **Total Unique Colleges** | **>= 501** | **1,129** | **PASS** |
| **All Tamil Nadu Districts** | **38 / 38** | **38 / 38 (100%)** | **PASS** |
| **Districts with College Records** | **38 / 38** | **38 / 38 (100%)** | **PASS** |
| **Government Colleges** | **>= 101** | **119** | **PASS** |
| **Government-Aided Colleges** | **>= 101** | **134** | **PASS** |
| **Self-Financing Colleges** | **>= 101** | **776** | **PASS** |
| **Autonomous Colleges** | **>= 101** | **532** | **PASS** |
| **Cataloged Degree Programs** | - | **2,821** | **PASS** |
| **Audited Campus Facilities** | - | **7,938** | **PASS** |

#### Multi-Dimensional Institutional Taxonomy (2D)
EduVerse AI cleanly decouples ownership from academic autonomy:
1. **Primary Ownership Type** (`primary_college_type`):
   - `GOVERNMENT` (Public / State-run)
   - `GOVERNMENT_AIDED` (State grant-in-aid funded)
   - `SELF_FINANCING` (Private self-funded)
   - `OTHER` (Central Universities, Deemed Universities, Institutes of National Importance)
2. **Academic Autonomy Status** (`autonomous_status`):
   - `AUTONOMOUS` (UGC conferred curriculum autonomy)
   - `NON_AUTONOMOUS` (Affiliated university curriculum)

**Default Seeded Credentials:**
- **Admin Account**: `admin@eduverse.ac.in` | Password: `Admin@123`
- **Student Account**: `student@eduverse.ac.in` | Password: `Student@123`

### 6. Running the Application

Launch the Flask development server:

```bash
python run.py
```

Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## ML Workflow & Recommendation Algorithm

The recommendation engine uses a **Multi-Criteria Utility Scoring Model** grounded in **Content-Based Filtering (CBF)**.

### Mathematical Formulation

Given a student preference vector $\vec{u} = (\text{course}, \text{district}, \text{city}, \text{budget}, \text{type}, \text{facilities})$ and candidate college $C_j$:

$$\text{Recommendation Score}(C_j) = \sum_{i=1}^{5} w_i \times S_i(C_j, \vec{u})$$

Where weights sum to $1.0$ ($100\%$):

| Factor | Weight ($w_i$) | Component | Scoring Logic ($S_i$) |
| :--- | :---: | :--- | :--- |
| **Course Match** | $0.35$ | $S_{\text{course}}$ | $1.0$ if college offers exact program; $0.7$ if related discipline; $0.0$ otherwise. |
| **Location Affinity** | $0.25$ | $S_{\text{location}}$ | $1.0$ if preferred city matches; $0.85$ if preferred district matches; $0.25$ if within state. |
| **Budget Compatibility** | $0.20$ | $S_{\text{budget}}$ | If fee $\le$ budget: $1.0 - 0.15 \times \frac{\text{fee}}{\text{budget}}$. If fee $>$ budget: $\max(0, 1.0 - \frac{\text{fee} - \text{budget}}{\text{budget}})$. If fee missing: $0.5$ with audit notice. |
| **College Type Match** | $0.10$ | $S_{\text{type}}$ | $1.0$ if institution governance matches preferred type; $0.3$ otherwise. |
| **Facility Coverage** | $0.10$ | $S_{\text{facility}}$ | Jaccard coefficient: $\frac{|\text{Requested Facilities} \cap \text{College Facilities}|}{|\text{Requested Facilities}|}$. |

### Jupyter Research Notebook
A full 12-section research notebook is available at:
```
ml/notebooks/eduverse_recommendation.ipynb
```
Sections include problem formulation, missing-value analysis, multi-label binarizing with scikit-learn, monotonicity testing, and evaluation metrics.

---

## REST API Documentation

### Public Discovery Endpoints

#### `GET /api/colleges`
Returns paginated, filtered college list.
- **Parameters**: `query`, `course`, `district`, `city`, `college_type`, `max_fee`, `facilities`, `sort` (`name` | `fee_asc` | `fee_desc` | `recent`), `page`, `per_page`.
- **Response**:
```json
{
  "success": true,
  "colleges": [ ... ],
  "pagination": {
    "page": 1,
    "per_page": 9,
    "total": 17,
    "total_pages": 2,
    "has_next": true,
    "has_prev": false
  }
}
```

#### `GET /api/colleges/<id>`
Returns detailed institutional profile including degree programs, duration, fees, eligibility, and amenities.

#### `GET /api/courses` & `GET /api/districts`
Returns unique lists of available programs and districts for dropdown auto-population.

#### `GET /api/analytics`
Returns live dataset metrics and chart data for Chart.js.

### Recommendation Endpoint

#### `POST /api/recommend`
Computes content-based recommendations based on student preferences.
- **Request Body**:
```json
{
  "course": "MCA",
  "state": "Tamil Nadu",
  "district": "Chennai",
  "city": "Chennai",
  "budget": 100000,
  "college_type": "University Department",
  "facilities": ["Hostel", "Central Library", "Placement Cell"]
}
```
- **Response**:
```json
{
  "success": true,
  "count": 5,
  "disclaimer": "Recommendations are informational and depend on the quality and freshness of available data...",
  "recommendations": [
    {
      "college_id": 1,
      "college_name": "College of Engineering, Guindy (Anna University)",
      "score": 99.2,
      "matching_factors": [
        "✓ MCA program is offered at this institution.",
        "✓ Located directly in your preferred city of Chennai.",
        "✓ Within your specified annual budget ceiling of ₹100,000 (starting at ₹35,000).",
        "✓ Matches your preferred institution type (University Department)."
      ],
      "fee": 35000.0,
      "location": "Chennai, Chennai",
      "data_status": "VERIFIED"
    }
  ]
}
```

### Comparison Endpoints

- `GET /api/compare`: Retrieve current colleges in matrix.
- `POST /api/compare`: Add college by numeric `college_id`.
- `DELETE /api/compare/<id>`: Remove college from matrix.
- `POST /api/compare/clear`: Clear comparison matrix.

### Authentication Endpoints

- `POST /api/auth/register`: Register new student account.
- `POST /api/auth/login`: Authenticate and set session cookie.
- `POST /api/auth/logout`: Terminate session.

### Admin Management Endpoints (Admin Privileges Required)

- `POST /api/admin/colleges`: Create new college with courses and facilities.
- `PUT /api/admin/colleges/<id>`: Update institutional profile and data status.
- `DELETE /api/admin/colleges/<id>`: Delete college (cascades to courses and facilities).

---

## Testing & Quality Assurance

EduVerse AI includes an automated test suite implemented in **pytest** containing **30 tests** covering authentication, exploration, filters, recommender scoring, comparison matrices, analytics, and admin role enforcement.

### Running Automated Tests

Execute pytest from the project root:

```bash
# Run full test suite with verbose output
pytest -v

# Run specific test modules
pytest tests/test_auth.py -v
pytest tests/test_colleges.py -v
pytest tests/test_recommendations.py -v
pytest tests/test_comparison.py -v
pytest tests/test_analytics.py -v
pytest tests/test_admin.py -v
```

### Test Results Summary
```
============================= test session starts =============================
tests/test_admin.py::test_unauthenticated_and_student_blocked_from_admin PASSED [  3%]
tests/test_admin.py::test_admin_dashboard_access_allowed PASSED          [  6%]
tests/test_admin.py::test_admin_college_crud_lifecycle PASSED            [ 10%]
tests/test_analytics.py::test_analytics_metrics_valid_dataset PASSED     [ 13%]
tests/test_analytics.py::test_analytics_page_html_render PASSED          [ 16%]
tests/test_analytics.py::test_analytics_empty_database_handling PASSED   [ 20%]
tests/test_auth.py::test_user_password_hashing PASSED                    [ 23%]
tests/test_auth.py::test_student_registration_success PASSED             [ 26%]
tests/test_auth.py::test_registration_duplicate_email PASSED             [ 30%]
tests/test_auth.py::test_registration_validation_errors PASSED           [ 33%]
tests/test_auth.py::test_user_login_success_and_logout PASSED            [ 36%]
tests/test_auth.py::test_user_login_invalid_credentials PASSED           [ 40%]
tests/test_colleges.py::test_explore_page_render PASSED                  [ 43%]
tests/test_colleges.py::test_api_colleges_list_and_pagination PASSED     [ 46%]
tests/test_colleges.py::test_search_by_college_name PASSED               [ 50%]
tests/test_colleges.py::test_filter_by_course PASSED                     [ 53%]
tests/test_colleges.py::test_filter_by_district PASSED                   [ 56%]
tests/test_colleges.py::test_filter_by_max_fee PASSED                    [ 60%]
tests/test_colleges.py::test_college_detail_valid_and_invalid_id PASSED  [ 63%]
tests/test_colleges.py::test_courses_and_districts_metadata_apis PASSED  [ 66%]
tests/test_comparison.py::test_add_to_comparison_and_retrieve PASSED     [ 70%]
tests/test_comparison.py::test_comparison_duplicate_prevention PASSED    [ 73%]
tests/test_comparison.py::test_comparison_maximum_four_colleges PASSED   [ 76%]
tests/test_comparison.py::test_comparison_remove_and_clear PASSED        [ 80%]
tests/test_comparison.py::test_compare_html_page_render PASSED           [ 83%]
tests/test_recommendations.py::test_recommendation_valid_input_and_structure PASSED [ 86%]
tests/test_recommendations.py::test_recommendation_ranking_order PASSED  [ 90%]
tests/test_recommendations.py::test_recommendation_invalid_budget PASSED [ 93%]
tests/test_recommendations.py::test_recommendation_no_matching_course PASSED [ 96%]
tests/test_recommendations.py::test_recommendation_empty_preferences_handled PASSED [100%]
============================= 30 passed in 11.26s =============================
```

---

## Data Quality & Transparency Model

EduVerse AI strictly enforces academic data integrity:
- **No Coerced Zeroes**: An unknown fee is stored as `NULL` and rendered as *"Information not available"*, rather than `0` (which would falsely imply a free college).
- **Audit Traces**: Every college record maintains its `source_url` and `last_updated` verification timestamp.
- **Data Status Labels**:
  - `VERIFIED`: Sourced directly from official college portals or government gazettes.
  - `ESTIMATED`: Standard fee norms based on state fee regulatory committee benchmarks.
  - `SAMPLE`: Synthetic records created to test edge cases (clearly labeled *"SAMPLE DATA — FOR DEVELOPMENT ONLY"*).
  - `NOT_AVAILABLE`: Acknowledged missing information.

---

## Tamil Nadu 38-District Statewide Coverage

EduVerse AI provides normalized, database-driven coverage for **all 38 official districts of Tamil Nadu**:

1. Ariyalur
2. Chengalpattu
3. Chennai
4. Coimbatore
5. Cuddalore
6. Dharmapuri
7. Dindigul
8. Erode
9. Kallakurichi
10. Kancheepuram
11. Kanniyakumari
12. Karur
13. Krishnagiri
14. Madurai
15. Mayiladuthurai
16. Nagapattinam
17. Namakkal
18. Perambalur
19. Pudukkottai
20. Ramanathapuram
21. Ranipet
22. Salem
23. Sivaganga
24. Tenkasi
25. Thanjavur
26. Theni
27. Thoothukudi
28. Tiruchirappalli
29. Tirunelveli
30. Tirupathur
31. Tiruppur
32. Tiruvallur
33. Tiruvannamalai
34. Tiruvarur
35. The Nilgiris
36. Vellore
37. Viluppuram
38. Virudhunagar

### District Coverage vs. College-Data Availability
- **Statewide District Support (38 / 38)**: Every one of Tamil Nadu's 38 revenue districts is maintained in the normalized `districts` reference table (`id`, `name`, `state`, `created_at`) with strict foreign key integrity (`colleges.district_id -> districts.id`).
- **Data Availability Differentiation**: While all 38 districts are supported in filters, dropdowns, APIs, and analytics, college-data availability varies realistically by district.
- **Zero-Data Transparency**: When a district currently has no cataloged college records in the database:
  - **Explorer (`/explore`)**: Transparently displays: *"College information not available for this district."*
  - **AI Recommender (`/api/recommend`)**: Responds with: `{"success": true, "recommendations": [], "message": "No college information is currently available for the selected district."}`.
  - **Analytics (`/analytics`)**: Distinguishes between reality and data ingestion with the wording: *"0 colleges currently available in EduVerse database"*.
  - **Map (`/map`)**: Reports *"No Mapped College Records Available"* without fabricating markers or fake coordinates.

### District Coverage Verification Command
Validate that all 38 districts exist in the database with zero missing records at any time:
```powershell
python seed/validate_districts.py
```
**Expected Output:**
```
Total Tamil Nadu districts: 38
Districts present: 38
Districts missing: 0

District coverage:
38 / 38 [OK]
```

---

## Security Architecture

1. **SQL Injection Prevention**: 100% parameterized queries using SQLAlchemy ORM.
2. **CSRF Protection**: Flask-WTF tokens enabled for web forms; API fetch calls pass `X-CSRFToken` headers.
3. **Password Security**: Passwords hashed with PBKDF2-HMAC-SHA256 via Werkzeug. Plaintext passwords are never stored.
4. **Server-Side Authorization**: `@admin_required` decorators verify user session roles server-side.
5. **Secrets Management**: Sensitive credentials isolated in `.env` (excluded via `.gitignore`).

---

## Known Limitations

1. **Fee Schedule Volatility**: Tuition fees in self-financing institutions are updated annually through government fee committee notifications and require periodic admin auditing.
2. **Admission Quota Separation**: TNEA single-window counseling vs. management quota seats have distinct fee tiers that can be expanded in future versions.
3. **Initial Scope**: Currently restricted to Tamil Nadu higher education institutions.

---

## Future Enhancements Roadmap

- **Pan-India Expansion**: Scalable architecture ready to support other states, districts, and university directorates.
- **Cutoff Tracker**: Ingest past years' TANCET and TNEA opening/closing ranks.
- **Natural Language Assistant**: Integrate LLM chat capabilities for natural-language college advising.
- **Batch CSV/Excel Importer**: Admin interface to upload bulk college data from university annual reports.

---

## Project Structure

```
eduverse_ai/
│
├── app/
│   ├── __init__.py                # Application Factory & Extension setup
│   │
│   ├── models/                    # Normalized SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── user.py                # User entity & password hashing
│   │   ├── college.py             # College profile & data status
│   │   ├── course.py              # Degree courses, fees & duration
│   │   ├── facility.py            # Campus amenities & infrastructure
│   │   ├── preference.py          # Student preference vectors
│   │   └── comparison.py          # Comparison list persistence
│   │
│   ├── routes/                    # Blueprint controllers
│   │   ├── __init__.py
│   │   ├── main.py                # Landing page
│   │   ├── auth.py                # Login, Register, Logout
│   │   ├── colleges.py            # Explorer, Detail, Map views & APIs
│   │   ├── comparison.py          # Side-by-side comparison matrix
│   │   ├── recommendations.py     # AI Recommender views & API
│   │   ├── analytics.py           # Real-time analytics dashboard
│   │   └── admin.py               # Admin console & CRUD APIs
│   │
│   ├── services/                  # Decoupled business logic
│   │   ├── __init__.py
│   │   ├── college_service.py     # Parameterized search & pagination
│   │   ├── comparison_service.py  # Matrix business rules & limits
│   │   ├── recommendation_service.py # Preference processing
│   │   └── analytics_service.py   # Live database aggregations
│   │
│   ├── recommender/               # Intelligent scoring & ML
│   │   ├── __init__.py
│   │   ├── feature_engineering.py # DataFrame vectorization
│   │   ├── recommender.py         # ContentBasedRecommender
│   │   └── scoring.py             # Multi-Criteria Weighted Model
│   │
│   ├── templates/                 # Jinja2 Templates
│   │   ├── base.html              # Base layout with Tailwind & Leaflet
│   │   ├── index.html             # Landing page with live database KPI
│   │   ├── login.html             # Sign in view
│   │   ├── register.html          # Student registration view
│   │   ├── explore.html           # College Explorer with filters
│   │   ├── college_detail.html    # Profile, courses & Leaflet map
│   │   ├── compare.html           # 2-4 matrix comparison table
│   │   ├── recommendations.html   # AI Recommender form & factor results
│   │   ├── analytics.html         # Chart.js dashboards
│   │   ├── map.html               # Dedicated Tamil Nadu campus map
│   │   ├── admin/
│   │   │   ├── dashboard.html     # Admin college directory
│   │   │   └── college_form.html  # Create & Edit college form
│   │   ├── errors/
│   │   │   ├── 403.html           # Access forbidden
│   │   │   ├── 404.html           # Page not found
│   │   │   └── 500.html           # Internal server error
│   │   └── components/
│   │       ├── navbar.html        # Sticky responsive navbar
│   │       ├── footer.html        # Footer with ethics disclosure
│   │       ├── college_card.html  # Card component with status badge
│   │       ├── data_status_badge.html # Semantic status pill
│   │       ├── empty_state.html   # SVG empty state
│   │       ├── alert.html         # Accessible alert banner
│   │       ├── loading.html       # Loading spinner
│   │       ├── pagination.html    # ARIA-accessible pagination
│   │       └── filter_panel.html  # Filter wrapper
│   │
│   ├── static/                    # Static Assets
│   │   ├── css/
│   │   │   └── styles.css         # Accessible styling & focus rings
│   │   └── js/
│   │       ├── explore.js         # Explorer controller
│   │       ├── compare.js         # Comparison utilities
│   │       ├── recommendations.js # Recommender controller
│   │       ├── analytics.js       # Chart.js configurations
│   │       └── map.js             # Leaflet.js Tamil Nadu map
│   │
│   └── utils/
│       ├── decorators.py          # @admin_required, @login_required
│       └── validators.py          # Payload & email validation
│
├── ml/                            # Machine Learning Research
│   └── notebooks/
│       └── eduverse_recommendation.ipynb # 12-section research notebook
│
├── migrations/                    # Flask-Migrate / Alembic version scripts
│
├── tests/                         # Pytest test suite (30 tests)
│   ├── conftest.py                # Fixtures
│   ├── test_auth.py               # Auth & security tests
│   ├── test_colleges.py           # Explorer & detail tests
│   ├── test_recommendations.py    # Scoring & factor tests
│   ├── test_comparison.py         # Comparison matrix tests
│   ├── test_analytics.py          # Analytics aggregations tests
│   └── test_admin.py              # Admin CRUD & authorization tests
│
├── seed/
│   └── seed_data.py               # Tamil Nadu seed dataset
│
├── config.py                      # Development, Testing, Production configs
├── run.py                         # Application entrypoint
├── pytest.ini                     # Pytest configuration
├── requirements.txt               # Pinned dependencies
├── .env.example                   # Environment variable template
├── .gitignore                     # Git exclusions
└── README.md                      # Documentation
```

---

## Academic Viva Explanation Guide

### How to Explain EduVerse AI in your MCA Viva:

1. **How EduVerse AI Works (Core Workflow)**:
   ```
   Student
     ↓
   Enters Desired Course, Budget Ceiling, District & Amenities
     ↓
   Flask Backend (POST /api/recommend)
     ↓
   SQLAlchemy ORM Queries Tamil Nadu Candidate Dataset
     ↓
   Feature Processing & Scoring Engine (Multi-Criteria Utility Model)
     ↓
   Ranked Match Percentages + Human-Readable Explanations
     ↓
   Side-by-Side Comparison Matrix / Interactive Leaflet Map
     ↓
   Student Makes Verified Educational Decision
   ```

2. **Key Viva Questions & Answers**:
   - **Q: Why Content-Based Filtering instead of Collaborative Filtering?**
     *A*: Educational admissions exhibit an inherent cold-start problem. Students choose a college once every few years, so continuous user-item interaction matrices (like Netflix or Amazon) do not exist. Content-Based Filtering models factual institutional attributes directly against user criteria without requiring fake synthetic ratings.
   - **Q: How are missing fees handled?**
     *A*: Rather than treating missing values as ₹0 (which would falsely imply a free institution), EduVerse AI stores missing values as `NULL`, applies a neutral confidence penalty in recommendation scoring, and flags an audit note advising the student to verify with the admissions office.
   - **Q: How does comparison avoid bias?**
     *A*: Unlike commercial lead-generation portals, EduVerse AI never declares an arbitrary "Winner" or "Rank #1". It presents factual columns side-by-side so students and parents can evaluate based on their individual family budget and location preferences.

---

## Author & Project Information

- **Project**: MCA Final-Year Project
- **Application**: EduVerse AI: Smart College Recommendation System for Tamil Nadu
- **Year**: 2026
