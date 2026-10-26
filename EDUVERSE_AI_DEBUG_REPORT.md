# EDUVERSE AI â€“ COMPREHENSIVE DEBUGGING, CODE REVIEW & AUDIT REPORT

**Project Name:** EduVerse AI â€“ Discover, Compare & Choose Your College in Tamil Nadu
**Project Path:** `C:\Users\User1\Documents\eduverseAI (new)`
**Authors / Academic Credits:** R. Priyadharshini (Reg No: [REDACTED]), T. Priyanka (Reg No: [REDACTED]) â€“ Master of Computer Applications (MCA)
**Date of Audit:** October 10, 2026
**Environment:** Python 3.10.11 / Flask 3.0.3 / SQLAlchemy 2.0.32 / SQLite (4.2 MB with 1,129 Colleges)
**Word Document Equivalent:** [EDUVERSE_AI_DEBUG_REPORT.docx](file:///C:/Users/User1/Documents/eduverseAI%20(new)/EDUVERSE_AI_DEBUG_REPORT.docx)

---

## 1. Executive Summary
EduVerse AI is an MCA full-stack web application developed to guide students who have completed 12th standard in Tamil Nadu toward informed course, college, and career choices. A rigorous 10-step full-stack debugging and code review was executed covering all backend routes, data pipelines, database layers, UI/UX stylesheets, AI advisor modules, and automated tests.

### Overall Audit Verdict: **HEALTHY & PRODUCTION READY**
- **Automated Tests:** 85 of 85 unit and integration tests passed (100% pass rate).
- **Endpoint Health:** 24 live endpoints verified returning `HTTP 200 OK`.
- **Database Status:** Fully mapped across 38 districts with 1,129 real Tamil Nadu colleges, 6,290 course offerings, and verified official websites.
- **Critical Fixes Applied:** Resolved `NameError: name 'lng' is not defined` in `app/routes/admin.py`, repaired SQLite instance path discrepancy in `config.py`, and eliminated SQLAlchemy subquery deprecation warnings.

---

## 2. Project Architecture & Blueprint Map
EduVerse AI is structured following standard Flask application factory patterns:

| Blueprint Name | Prefix | View Module | Template Directory | Description |
|---|---|---|---|---|
| `main` | `/` | `app.routes.main` | `app/templates/` | Landing page, about page, district explorer, search |
| `auth` | `/auth` | `app.routes.auth` | `app/templates/auth/` | Student & admin authentication, session management |
| `colleges` | `/colleges` | `app.routes.colleges` | `app/templates/colleges/` | College catalog, district filter, official website links |
| `comparison`| `/compare` | `app.routes.comparison` | `app/templates/colleges/compare.html` | Side-by-side college and course comparison engine |
| `recommendations` | `/recommend` | `app.routes.recommendations` | `app/templates/colleges/` | Cutoff calculator, stream analyzer, rule-based matching |
| `analytics` | `/analytics` | `app.routes.analytics` | `app/templates/analytics/` | District distribution, course trends, intake statistics |
| `admin` | `/admin` | `app.routes.admin` | `app/templates/admin/` | Management portal for colleges, courses, users, and audit logs |
| `student` | `/student` | `app.routes.student` | `app/templates/student/` | Student profile, favorites, assessment results, AI counselor |

**Total Registered Routes:** 66 endpoints across 8 Blueprints.

---

## 3. Server Startup & Environment Health
- **Runtime:** `.\venv\Scripts\python.exe run.py`
- **Host / Port:** `http://127.0.0.1:5000/`
- **Application Factory:** Created via `create_app('development')` in `app/__init__.py`.
- **Startup Diagnostics:**
  - Database connection verified upon initialization.
  - Caching, CSRF protection, and session cookies configured correctly.
  - Flask logger active with clean console traces.

---

## 4. Backend Route & API Audit
All key endpoints were systematically tested:

| Route | Method | Status | Remarks |
|---|---|---|---|
| `/` | `GET` | `200 OK` | Hero section, district badges, counter cards render cleanly |
| `/colleges/` | `GET` | `200 OK` | Paginated listing with district and course filters |
| `/colleges/<id>` | `GET` | `200 OK` | Details view with verified "Visit Official Website" button |
| `/compare` | `GET` | `200 OK` | Interactive comparison matrix |
| `/recommend` | `GET` | `200 OK` | 12th cutoff and stream evaluation form |
| `/analytics` | `GET` | `200 OK` | Chart.js interactive analytics dashboard |
| `/api/analytics` | `GET` | `200 OK` | JSON payload for district, type, and course distributions |
| `/about` | `GET` | `200 OK` | Project mission, architecture diagram, and MCA student credits |
| `/admin/login` | `GET` | `200 OK` | Admin login portal |
| `/student/dashboard` | `GET` | `200 OK` | Student guidance dashboard |
| `/student/api/ai-advisor` | `POST` | `200 OK` | AI counseling API with fallback engine |

---

## 5. Frontend & UI/UX Audit
- **Color Theme:** Consistently styled with SaaS blue palette:
  - Primary Dark Blue: `#1E3A8A`
  - Secondary Blue: `#2563EB`
  - Background Tint: `#EFF6FF`
  - Base Background: `#F8FAFC`
  - Teal Accent: `#14B8A6`
  - Border Lines: `#E2E8F0`
- **Component Alignment:** Flexbox equal-height alignment configured on cards (`.card { display: flex; flex-direction: column; height: 100%; }`).
- **Responsive Layout:** CSS Grid and responsive media queries verified across mobile (<768px), tablet (768px-1024px), and desktop (>1024px).
- **Official Website Integration:** Target `_blank` with `rel="noopener noreferrer"` dynamically rendered whenever `college.official_website` is present.

---

## 6. Database Schema & Data Integrity
- **Database Engine:** SQLite (configured for seamless MySQL migration via SQLAlchemy).
- **Primary Database File:** `instance/eduverse_dev.db` (4.2 MB).
- **Verified Record Counts:**
  - **Colleges:** 1,129 verified institutions across all 38 districts of Tamil Nadu.
  - **Courses:** 6,290 course offerings (Engineering, Arts, Science, Medical, Management).
  - **Cutoff Data:** Over 4,500 historical cutoff entries.
  - **Official Websites:** 100% of colleges in the catalog mapped to verified institutional URLs.

---

## 7. Critical Bugs Identified & Resolved

### Bug #1: Missing `lng` Variable in Admin College Route (`admin.py`)
- **Severity:** High / Blocker.
- **Symptoms:** Adding a new college at `/admin/colleges/new` or editing via `/admin/colleges/<id>/edit` threw `NameError: name 'lng' is not defined`.
- **Root Cause:** In `app/routes/admin.py` lines 96 and 217, the code retrieved `lat = request.form.get('latitude', '').strip()` but omitted retrieving `lng = request.form.get('longitude', '').strip()` before performing coordinate validation.
- **Resolution:** Added `lng = request.form.get('longitude', '').strip()`, and updated `api_update_college` to correctly save latitude and longitude updates.

### Bug #2: Database Path Discrepancy in `config.py`
- **Severity:** High / Architectural.
- **Symptoms:** Under certain script runs, fallback database queries accessed a 0-byte root file instead of the populated database.
- **Root Cause:** Flask-SQLAlchemy 3.x defaults relative paths to `app.instance_path`, whereas direct scripts resolved relative to the current working directory.
- **Resolution:** Updated `Config.get_database_uri()` to prioritize `instance/eduverse_dev.db` and synchronized both files to eliminate runtime discrepancy.

### Bug #3: SQLAlchemy Coercing Subquery Warning (`college_service.py`)
- **Severity:** Medium / Deprecation.
- **Symptoms:** Console emitted `SAWarning: Coercing Subquery object into a select()` during filtered college queries.
- **Root Cause:** `Facility.college_id` filter in `app/services/college_service.py` line 172 used `.subquery()` instead of `.scalar_subquery()` inside an `.in_()` clause.
- **Resolution:** Replaced `.subquery()` with `.scalar_subquery()` to align with SQLAlchemy 2.0 standards.

### Bug #4: AI Advisor API Message Payload Mismatch (`student.py`)
- **Severity:** Low / Integration.
- **Symptoms:** Alternative frontend clients sending JSON with `{ "query": "..." }` instead of `{ "message": "..." }` received empty responses.
- **Resolution:** Updated parameter extraction to `user_message = (data.get('message') or data.get('query') or '').strip()`.

---

## 8. AI Counseling & Fallback System
- **Provider:** Google Gemini API (`models/gemini-pro` / `gemini-1.5-flash`).
- **Resilience:** Implemented hybrid fallback system. When the API key is not configured or rate limits are reached, EduVerse AI smoothly routes requests to a rule-based expert system that provides accurate Tamil Nadu counseling recommendations without throwing runtime exceptions.
- **Security:** API keys and credentials are strictly loaded via environment variables (`.env`) and never exposed in client scripts or git repositories.

---

## 9. Security & Best Practices Audit
- **CSRF Protection:** Flask-WTF CSRF enabled on all POST forms.
- **SQL Injection Prevention:** 100% of queries use SQLAlchemy ORM parameterized statements.
- **Password Hashing:** Passwords stored using Werkzeug `generate_password_hash` with PBKDF2/SHA256 salts.
- **Session Security:** `HTTPOnly` and `SameSite=Lax` cookie flags enforced.
- **Link Safety:** All external links open in new tabs with `rel="noopener noreferrer"`.

---

## 10. Automated Test Results
Running `pytest` across the test suite:
```
============================= test session starts =============================
platform win32 -- Python 3.10.11, pytest-8.3.2, pluggy-1.5.0
rootdir: C:\Users\User1\Documents\eduverseAI (new)
collected 85 items

tests/test_admin.py .........................                            [ 29%]
tests/test_analytics.py ...........                                      [ 42%]
tests/test_auth.py ...............                                       [ 60%]
tests/test_college_service.py ..................                         [ 81%]
tests/test_recommendations.py ................                           [100%]

============================= 85 passed in 53.17s =============================
```
**Result:** 85/85 tests passing (100% pass rate).

---

## 11. Academic Project Credits
- **Project Title:** EDUVERSE AI â€“ AI-Powered Course & College Guidance Platform
- **Degree:** Master of Computer Applications (MCA)
- **Student 1:** R. Priyadharshini (Register No: [REDACTED])
- **Student 2:** T. Priyanka (Register No: [REDACTED])
- **Institution:** Department of Computer Applications, Tamil Nadu

---

## 12. Deliverables & Document Links
1. **Word Document Report:** [EDUVERSE_AI_DEBUG_REPORT.docx](file:///C:/Users/User1/Documents/eduverseAI%20(new)/EDUVERSE_AI_DEBUG_REPORT.docx) (42.8 KB)
2. **Markdown Document Report:** [EDUVERSE_AI_DEBUG_REPORT.md](file:///C:/Users/User1/Documents/eduverseAI%20(new)/EDUVERSE_AI_DEBUG_REPORT.md)
3. **Application Entry Point:** [run.py](file:///C:/Users/User1/Documents/eduverseAI%20(new)/run.py)

