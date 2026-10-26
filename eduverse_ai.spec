# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from pathlib import Path

block_cipher = None

BASE_DIR = Path(os.path.abspath('.')).resolve()

datas = [
    (str(BASE_DIR / 'app' / 'templates'), 'app/templates'),
    (str(BASE_DIR / 'app' / 'static'), 'app/static'),
    (str(BASE_DIR / 'instance' / 'eduverse_dev.db'), 'instance'),
]

# Include .env if exists
if (BASE_DIR / '.env').exists():
    datas.append((str(BASE_DIR / '.env'), '.'))

# Include root fallback db if exists
if (BASE_DIR / 'eduverse_dev.db').exists():
    datas.append((str(BASE_DIR / 'eduverse_dev.db'), '.'))

hidden_imports = [
    'app',
    'app.models',
    'app.models.user',
    'app.models.district',
    'app.models.college',
    'app.models.course',
    'app.models.facility',
    'app.models.preference',
    'app.models.comparison',
    'app.models.dataset_metadata',
    'app.models.student_query',
    'app.models.student_login_activity',
    'app.models.student_feedback',
    'app.models.student_profile',
    'app.routes',
    'app.routes.main',
    'app.routes.auth',
    'app.routes.colleges',
    'app.routes.comparison',
    'app.routes.recommendations',
    'app.routes.analytics',
    'app.routes.admin',
    'app.routes.student',
    'app.services',
    'app.services.college_service',
    'app.services.assessment_service',
    'app.services.recommendation_service',
    'app.services.analytics_service',
    'app.services.ai_counselor_service',
    'app.services.student_analytics_service',
    'app.recommender',
    'app.recommender.recommender',
    'app.recommender.scoring',
    'app.recommender.feature_engineering',
    'app.utils',
    'app.utils.validators',
    'app.utils.decorators',
    'app.utils.district_normalizer',
    'config',
    'sqlalchemy',
    'sqlalchemy.orm',
    'sqlalchemy.dialects.sqlite',
    'sqlalchemy.dialects.mysql',
    'pymysql',
    'cryptography',
    'email_validator',
    'sklearn',
    'sklearn.utils._typedefs',
    'pandas',
    'numpy',
    'jinja2',
    'werkzeug',
    'werkzeug.security',
    'flask',
    'flask_sqlalchemy',
    'flask_migrate',
    'flask_wtf',
    'flask_wtf.csrf',
    'dotenv',
]

a = Analysis(
    ['run.py'],
    pathex=[str(BASE_DIR)],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['pytest', 'tests'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='EduVerse_AI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
