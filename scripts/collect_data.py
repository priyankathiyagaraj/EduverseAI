import os
import re
import json
from pathlib import Path
import pypdf

BASE_DIR = Path(__file__).resolve().parent.parent
PDF_PATH = Path(r"C:\Users\User1\.gemini\antigravity\brain\e50edd85-aef7-4369-934a-1e2c2b3b6191\.user_uploaded\media_1790086306073.pdf")
OUTPUT_RAW_DIR = BASE_DIR / "data" / "raw"
OUTPUT_RAW_FILE = OUTPUT_RAW_DIR / "pdf_colleges.json"

STANDARD_CATEGORIES = {'Engineering & Technology', 'Arts & Science', 'Medical & Allied Health Science'}

def extract_colleges_from_pdf():
    print(f"Reading PDF from {PDF_PATH}...")
    reader = pypdf.PdfReader(str(PDF_PATH))
    total_pages = len(reader.pages)
    print(f"Total pages: {total_pages}")

    colleges = []
    for p_idx, page in enumerate(reader.pages):
        lines = [l.strip() for l in page.extract_text().split('\n') if l.strip()]
        i = 0
        while i < len(lines):
            if re.match(r'^\d+$', lines[i]):
                s_no = int(lines[i])
                i += 1
                name_parts = []
                while i < len(lines):
                    if i + 1 < len(lines) and lines[i+1] in STANDARD_CATEGORIES:
                        district = lines[i]
                        category = lines[i+1]
                        i += 2
                        break
                    else:
                        name_parts.append(lines[i])
                        i += 1
                full_name = ' '.join(name_parts)
                colleges.append({
                    's_no': s_no,
                    'name': full_name,
                    'district': district,
                    'category': category,
                    'page': p_idx + 1,
                    'source': 'Master Directory of 1000 Higher Education Institutions in Tamil Nadu'
                })
            else:
                i += 1

    OUTPUT_RAW_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_RAW_FILE, 'w', encoding='utf-8') as f:
        json.dump(colleges, f, indent=2, ensure_ascii=False)

    print(f"Successfully extracted {len(colleges)} colleges into {OUTPUT_RAW_FILE}")
    return colleges

if __name__ == '__main__':
    extract_colleges_from_pdf()
