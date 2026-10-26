with open('generate_final_documentation.py', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Tamil abstract font size
old_tamil = """    p_tabs = doc.add_paragraph(
        "பன்னிரண்டாம் வகுப்பு பொதுத்தேர்வை முடித்த மாணவர்கள் தங்களின் அடுத்தகட்ட உயர்கல்வி மற்றும் கல்லூரிப் பிரிவை தேர்ந்தெடுப்பது என்பது அவர்களின் எதிர்கால "
        "வாழ்க்கையை தீர்மானிக்கும் மிக முக்கியமான முடிவாகும். தமிழ்நாட்டில் உள்ள 38 மாவட்டங்களில் ஆயிரத்திற்கும் மேற்பட்ட அரசு, அரசு உதவிபெறும், தனியார் சுயநிதி "
        "மற்றும் தன்னாட்சிப் (Autonomous) பொறியியல், கலை மற்றும் அறிவியல் கல்லூரிகள் இயங்கி வருகின்றன. இத்தகைய பரந்த கல்விச் சூழலில், மாணவர்கள் தங்களின் மதிப்பெண்கள், "
        "ஆர்வங்கள் மற்றும் இருப்பிடத்திற்கு ஏற்ற சிறந்த கல்லூரிகளை கண்டறிவதில் போதிய விழிப்புணர்வின்மையும், சரியான வழிகாட்டலின்மையும் பெரும் சவாலாக உள்ளது. பல வணிக "
        "நோக்குடைய இணையதளங்கள் முழுமையற்ற மற்றும் விளம்பரச் சார்புடைய தகவல்களையே வழங்குகின்றன.\\n\\n"
        "இச்சிக்கல்களுக்குத் தீர்வாக, EduVerse AI என்ற முழுமையான, செயற்கை நுண்ணறிவு (Artificial Intelligence) சார்ந்த உயர்கல்வி வழிகாட்டுதல் மற்றும் கல்லூரி ஒப்பீட்டு "
        "வலைப்பின்னல் தளம் உருவாக்கப்பட்டுள்ளது. இத்தளம் பைதான் பிளாஸ்க் (Python Flask) கட்டமைப்பிலும், SQL தரவுத்தள (Database) அடிப்படையிலும், HTML, CSS மற்றும் "
        "ஜாவாஸ்கிரிப்ட் (JavaScript) தொழில் நுட்பங்களுடனும் கட்டமைக்கப்பட்டுள்ளது. இதில் தமிழ்நாட்டின் அனைத்து 38 மாவட்டங்களிலும் உள்ள 1,129 அங்கீகரிக்கப்பட்ட கல்லூரிகள் "
        "மற்றும் 8,120 பாடப்பிரிவுகளின் அதிகாரப்பூர்வ விபரங்கள், அமைவிடம் மற்றும் சரிபார்க்கப்பட்ட அதிகாரப்பூர்வ இணையதள முகவரிகள் (Official Websites) ஒருங்கிணைக்கப்பட்டுள்ளன.\\n\\n"
        "மாணவர்கள் தங்கள் மாவட்டங்கள், கட்டண வரம்புகள், தன்னாட்சி அந்தஸ்து மற்றும் பாடப்பிரிவுகளின் அடிப்படையில் கல்லூரிகளை தேடவும் (Search & Filter), பல கல்லூரிகளை ஒரே "
        "திரையில் ஒப்பிட்டுப் பார்க்கவும் (College Comparison), மாவட்ட வாரியான கல்வி புள்ளிவிபரங்களை (Analytics) காணவும் முடியும். மேலும், 12-ஆம் வகுப்பு மதிப்பெண்களை "
        "உள்ளீடு செய்து TNEA பொறியியல் கலந்தாய்வு Cutoff மதிப்பெண்களை கணக்கிடும் முறையும், விருப்பங்களின் அடிப்படையில் கல்லூரிகளை வரிசைப்படுத்தி பரிந்துரைக்கும் "
        "(Recommendation Algorithm) அமைப்பும் இதில் நிறுவப்பட்டுள்ளது. கூகிள் ஜெமினி (Google Gemini API) மற்றும் விதிமுறை சார்ந்த ஆலோசனை இயந்திரம் (Rule-Based Counselor "
        "Engine) மூலம் மாணவர்கள் தங்களுக்குப் பொருத்தமான உயர்கல்வி மற்றும் வேலைவாய்ப்பு ஆலோசனைகளை நேரடியாகப் பெற முடிகிறது. இத்திட்டத்தின் செயல்முறைகள் 85 தானியங்கி "
        "சோதனைகள் (Pytest) மூலம் வெற்றிகரமாக சரிபார்க்கப்பட்டு 100% துல்லியத்துடன் இயங்குவது உறுதி செய்யப்பட்டுள்ளது."
    )
    p_tabs.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY"""

new_tamil = """    p_tabs = doc.add_paragraph()
    p_tabs.paragraph_format.line_spacing = 1.15
    p_tabs.paragraph_format.space_after = Pt(2)
    p_tabs.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    r_tabs = p_tabs.add_run(
        "பன்னிரண்டாம் வகுப்பு பொதுத்தேர்வை முடித்த மாணவர்கள் தங்களின் அடுத்தகட்ட உயர்கல்வி மற்றும் கல்லூரிப் பிரிவை தேர்ந்தெடுப்பது என்பது அவர்களின் எதிர்கால "
        "வாழ்க்கையை தீர்மானிக்கும் மிக முக்கியமான முடிவாகும். தமிழ்நாட்டில் உள்ள 38 மாவட்டங்களில் ஆயிரத்திற்கும் மேற்பட்ட அரசு, அரசு உதவிபெறும், தனியார் சுயநிதி "
        "மற்றும் தன்னாட்சிப் (Autonomous) பொறியியல், கலை மற்றும் அறிவியல் கல்லூரிகள் இயங்கி வருகின்றன. இத்தகைய பரந்த கல்விச் சூழலில், மாணவர்கள் தங்களின் மதிப்பெண்கள், "
        "ஆர்வங்கள் மற்றும் இருப்பிடத்திற்கு ஏற்ற சிறந்த கல்லூரிகளை கண்டறிவதில் போதிய விழிப்புணர்வின்மையும், சரியான வழிகாட்டலின்மையும் பெரும் சவாலாக உள்ளது. பல வணிக "
        "நோக்குடைய இணையதளங்கள் முழுமையற்ற மற்றும் விளம்பரச் சார்புடைய தகவல்களையே வழங்குகின்றன.\\n\\n"
        "இச்சிக்கல்களுக்குத் தீர்வாக, EduVerse AI என்ற முழுமையான, செயற்கை நுண்ணறிவு (Artificial Intelligence) சார்ந்த உயர்கல்வி வழிகாட்டுதல் மற்றும் கல்லூரி ஒப்பீட்டு "
        "வலைப்பின்னல் தளம் உருவாக்கப்பட்டுள்ளது. இத்தளம் பைதான் பிளாஸ்க் (Python Flask) கட்டமைப்பிலும், SQL தரவுத்தள (Database) அடிப்படையிலும், HTML, CSS மற்றும் "
        "ஜாவாஸ்கிரிப்ட் (JavaScript) தொழில் நுட்பங்களுடனும் கட்டமைக்கப்பட்டுள்ளது. இதில் தமிழ்நாட்டின் அனைத்து 38 மாவட்டங்களிலும் உள்ள 1,129 அங்கீகரிக்கப்பட்ட கல்லூரிகள் "
        "மற்றும் 8,120 பாடப்பிரிவுகளின் அதிகாரப்பூர்வ விபரங்கள், அமைவிடம் மற்றும் சரிபார்க்கப்பட்ட அதிகாரப்பூர்வ இணையதள முகவரிகள் (Official Websites) ஒருங்கிணைக்கப்பட்டுள்ளன.\\n\\n"
        "மாணவர்கள் தங்கள் மாவட்டங்கள், கட்டண வரம்புகள், தன்னாட்சி அந்தஸ்து மற்றும் பாடப்பிரிவுகளின் அடிப்படையில் கல்லூரிகளை தேடவும் (Search & Filter), பல கல்லூரிகளை ஒரே "
        "திரையில் ஒப்பிட்டுப் பார்க்கவும் (College Comparison), மாவட்ட வாரியான கல்வி புள்ளிவிபரங்களை (Analytics) காணவும் முடியும். மேலும், 12-ஆம் வகுப்பு மதிப்பெண்களை "
        "உள்ளீடு செய்து TNEA பொறியியல் கலந்தாய்வு Cutoff மதிப்பெண்களை கணக்கிடும் முறையும், விருப்பங்களின் அடிப்படையில் கல்லூரிகளை வரிசைப்படுத்தி பரிந்துரைக்கும் "
        "(Recommendation Algorithm) அமைப்பும் இதில் நிறுவப்பட்டுள்ளது. கூகிள் ஜெமினி (Google Gemini API) மற்றும் விதிமுறை சார்ந்த ஆலோசனை இயந்திரம் (Rule-Based Counselor "
        "Engine) மூலம் மாணவர்கள் தங்களுக்குப் பொருத்தமான உயர்கல்வி மற்றும் வேலைவாய்ப்பு ஆலோசனைகளை நேரடியாகப் பெற முடிகிறது. இத்திட்டத்தின் செயல்முறைகள் 85 தானியங்கி "
        "சோதனைகள் (Pytest) மூலம் வெற்றிகரமாக சரிபார்க்கப்பட்டு 100% துல்லியத்துடன் இயங்குவது உறுதி செய்யப்பட்டுள்ளது."
    )
    r_tabs.font.size = Pt(9.5)"""

if old_tamil in text:
    text = text.replace(old_tamil, new_tamil)
    print("Replaced Tamil abstract.")
else:
    print("Tamil abstract not matched.")

# 2. Preliminary tables styling
old_toc = """    for idx, (title, page) in enumerate(toc_items):
        r_title = t_toc.rows[idx].cells[0].paragraphs[0].add_run(title)
        r_page = t_toc.rows[idx].cells[1].paragraphs[0].add_run(page)
        t_toc.rows[idx].cells[1].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
        r_title.font.name = "Times New Roman"
        r_page.font.name = "Times New Roman"
        if "CHAPTER" in title or "APPENDICES" in title or "REFERENCES" in title:
            r_title.font.bold = True
            r_page.font.bold = True"""

new_toc = """    for idx, (title, page) in enumerate(toc_items):
        c0, c1 = t_toc.rows[idx].cells
        set_cell_margins(c0, top=15, bottom=15, left=30, right=30)
        set_cell_margins(c1, top=15, bottom=15, left=30, right=30)
        p0, p1 = c0.paragraphs[0], c1.paragraphs[0]
        p0.paragraph_format.space_after = Pt(1)
        p1.paragraph_format.space_after = Pt(1)
        r_title = p0.add_run(title)
        r_page = p1.add_run(page)
        p1.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        r_title.font.name = "Times New Roman"
        r_page.font.name = "Times New Roman"
        r_title.font.size = Pt(8.5)
        r_page.font.size = Pt(8.5)
        if "CHAPTER" in title or "APPENDICES" in title or "REFERENCES" in title:
            r_title.font.bold = True
            r_page.font.bold = True"""

if old_toc in text:
    text = text.replace(old_toc, new_toc)
    print("Replaced TOC styling.")
else:
    print("TOC styling not matched.")

# 3. List of Tables
old_lt = """    for i, (t_no, t_title, t_pg) in enumerate(tables_list):
        row = t_lt.rows[i + 1].cells
        row[0].paragraphs[0].add_run(t_no)
        row[1].paragraphs[0].add_run(t_title)
        row[2].paragraphs[0].add_run(t_pg)
        row[2].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT"""

new_lt = """    for row in t_lt.rows:
        for cell in row.cells:
            set_cell_margins(cell, top=15, bottom=15, left=30, right=30)
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(1)
            for r in p.runs:
                r.font.name = "Times New Roman"
                r.font.size = Pt(8.5)
    for i, (t_no, t_title, t_pg) in enumerate(tables_list):
        row = t_lt.rows[i + 1].cells
        r0 = row[0].paragraphs[0].add_run(t_no)
        r1 = row[1].paragraphs[0].add_run(t_title)
        r2 = row[2].paragraphs[0].add_run(t_pg)
        row[2].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
        for r in (r0, r1, r2):
            r.font.name = "Times New Roman"
            r.font.size = Pt(8.5)"""

if old_lt in text:
    text = text.replace(old_lt, new_lt)
    print("Replaced List of Tables.")
else:
    print("List of Tables not matched.")

# 4. List of Figures
old_lf = """    for i, (f_no, f_title, f_pg) in enumerate(figs_list):
        row = t_lf.rows[i + 1].cells
        row[0].paragraphs[0].add_run(f_no)
        row[1].paragraphs[0].add_run(f_title)
        row[2].paragraphs[0].add_run(f_pg)
        row[2].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT"""

new_lf = """    for row in t_lf.rows:
        for cell in row.cells:
            set_cell_margins(cell, top=15, bottom=15, left=30, right=30)
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(1)
            for r in p.runs:
                r.font.name = "Times New Roman"
                r.font.size = Pt(8.5)
    for i, (f_no, f_title, f_pg) in enumerate(figs_list):
        row = t_lf.rows[i + 1].cells
        r0 = row[0].paragraphs[0].add_run(f_no)
        r1 = row[1].paragraphs[0].add_run(f_title)
        r2 = row[2].paragraphs[0].add_run(f_pg)
        row[2].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.RIGHT
        for r in (r0, r1, r2):
            r.font.name = "Times New Roman"
            r.font.size = Pt(8.5)"""

if old_lf in text:
    text = text.replace(old_lf, new_lf)
    print("Replaced List of Figures.")
else:
    print("List of Figures not matched.")

# 5. List of Abbreviations
old_abb = """    for i, (ab, exp) in enumerate(abbr_list):
        row = t_abb.rows[i + 1].cells
        row[0].paragraphs[0].add_run(ab).font.bold = True
        row[1].paragraphs[0].add_run(exp)"""

new_abb = """    for row in t_abb.rows:
        for cell in row.cells:
            set_cell_margins(cell, top=15, bottom=15, left=30, right=30)
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(1)
            for r in p.runs:
                r.font.name = "Times New Roman"
                r.font.size = Pt(8.5)
    for i, (ab, exp) in enumerate(abbr_list):
        row = t_abb.rows[i + 1].cells
        r0 = row[0].paragraphs[0].add_run(ab)
        r0.font.bold = True
        r1 = row[1].paragraphs[0].add_run(exp)
        for r in (r0, r1):
            r.font.name = "Times New Roman"
            r.font.size = Pt(8.5)"""

if old_abb in text:
    text = text.replace(old_abb, new_abb)
    print("Replaced List of Abbreviations.")
else:
    print("List of Abbreviations not matched.")

# 6. Screenshot image width
text = text.replace('width=Inches(4.5)', 'width=Inches(3.8)')

with open('generate_final_documentation.py', 'w', encoding='utf-8') as f:
    f.write(text)

print('Calibration script completed.')
