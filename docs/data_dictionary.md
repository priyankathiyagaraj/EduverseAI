# EduVerse AI Data Dictionary & College Classification Methodology

## 1. Classification Methodology

Tamil Nadu higher education institutions possess both **ownership/governance dimensions** and **academic autonomy dimensions**. Conflating these two distinct dimensions causes inaccurate counting or inappropriate categorization.

In EduVerse AI, colleges are classified using a **two-dimensional orthogonal model**:

### Dimension 1: Primary Ownership (`primary_college_type`)
- **`GOVERNMENT`**: Fully funded, established, and administered directly by the Government of Tamil Nadu (through the Directorate of Collegiate Education - DCE, Directorate of Technical Education - DOTE, or Health & Family Welfare Department) or Central Government.
- **`GOVERNMENT_AIDED`**: Established by private educational trusts, missions, or philanthropic bodies, but receiving recurring salary grants-in-aid from the State Government for sanctioned teaching and non-teaching posts.
- **`SELF_FINANCING`**: Privately owned and self-supported institutions run by registered educational trusts or societies without direct government financial grants-in-aid.
- **`OTHER`**: Central institutions of national importance (e.g., IIT Madras, NIT Trichy), State University Departments/Constituent Campuses, or Deemed-to-be-Universities.
- **`UNKNOWN`**: Insufficient authoritative data available to determine ownership category.

### Dimension 2: Academic Autonomy Status (`autonomous_status`)
- **`AUTONOMOUS`**: Conferred autonomous status by the University Grants Commission (UGC) under the UGC Autonomous Colleges Regulations. Such colleges design their own curricula, conduct their own examinations, and publish their own results, while degrees are awarded by the affiliating university.
- **`NON_AUTONOMOUS`**: Affiliated non-autonomous institutions following university curricula, academic schedules, and centralized university examinations.
- **`UNKNOWN`**: Autonomy status not yet verified against UGC lists.

---

## 2. Table: `colleges`

| Column | Type | Nullable | Description & Constraints |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | No | Primary key, autoincrement |
| `name` | VARCHAR(255) | No | Official name of the college / institution |
| `normalized_name` | VARCHAR(255) | Yes | Standardized lowercase string without punctuation for deduplication |
| `code` | VARCHAR(50) | Yes | Official TNEA / AISHE / DOTE / Counseling code |
| `state` | VARCHAR(100) | No | State (defaults to 'Tamil Nadu') |
| `district_id` | INTEGER | Yes | Foreign Key to `districts.id` |
| `district` | VARCHAR(100) | No | Canonical district name |
| `city` | VARCHAR(100) | No | City or town where the campus is located |
| `college_type` | VARCHAR(100) | No | Display/legacy type (e.g. Government, Government-Aided, Self-Financing) |
| `primary_college_type` | VARCHAR(50) | No | Controlled vocabulary: `GOVERNMENT`, `GOVERNMENT_AIDED`, `SELF_FINANCING`, `OTHER`, `UNKNOWN` |
| `autonomous_status` | VARCHAR(50) | No | Controlled vocabulary: `AUTONOMOUS`, `NON_AUTONOMOUS`, `UNKNOWN` |
| `address` | TEXT | Yes | Physical campus address |
| `latitude` | FLOAT | Yes | Geographical latitude (-90.0 to 90.0) |
| `longitude` | FLOAT | Yes | Geographical longitude (-180.0 to 180.0) |
| `website` | VARCHAR(255) | Yes | Official website URL |
| `description` | TEXT | Yes | Institutional profile and academic background |
| `source_url` | VARCHAR(500) | Yes | Official portal or directory reference URL |
| `source_name` | VARCHAR(150) | Yes | Name of authoritative provider (e.g., DCE, UGC, TNEA, Official Website) |
| `source_type` | VARCHAR(50) | Yes | Source category: `OFFICIAL`, `GOVERNMENT_PORTAL`, `UNIVERSITY_PORTAL` |
| `source_classification`| VARCHAR(100) | Yes | Classification category code from the source |
| `classification_source`| VARCHAR(150) | Yes | Provenance source verifying the college type & autonomy |
| `data_status` | VARCHAR(50) | No | `VERIFIED`, `UNVERIFIED`, `ESTIMATED`, `SAMPLE` |
| `last_verified` | DATE | Yes | Date on which the data was verified against authoritative directories |
| `last_updated` | DATETIME | No | Last record update timestamp |
| `created_at` | DATETIME | No | Record creation timestamp |

---

## 3. Table: `dataset_metadata`

| Column | Type | Nullable | Description |
| :--- | :--- | :--- | :--- |
| `id` | INTEGER | No | Primary key, autoincrement |
| `dataset_version` | VARCHAR(50) | No | Semantic version of dataset (e.g., `1.0.0`, `2.0.0`) |
| `source` | VARCHAR(255) | No | Primary source documentation or compilation directory |
| `retrieved_at` | DATETIME | No | Ingestion timestamp |
| `total_records` | INTEGER | No | Total unique college records in dataset |
| `verified_records` | INTEGER | No | Total records verified against authoritative sources |
| `notes` | TEXT | Yes | Audit notes, pipeline parameters, and category breakdown summary |

---

## 4. Controlled Reference Data & Integrity Rules

1. **Foreign Key Integrity**:
   - `colleges.district_id` MUST reference `districts.id`.
   - `courses.college_id` MUST reference `colleges.id` (ON DELETE CASCADE).
   - `facilities.college_id` MUST reference `colleges.id` (ON DELETE CASCADE).
2. **Missing Information Policy**:
   - Fees, packages, or coordinates not confirmed by official publications MUST be stored as `NULL`.
   - UI displays "Information not available." rather than misleading placeholders or `0`.
3. **Idempotency Rule**:
   - Repeated ingestion of data files MUST NOT create duplicates.
   - Matching is performed on `(normalized_name, district_id)` or unique `code`.
