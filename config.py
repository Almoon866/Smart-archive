# -*- coding: utf-8 -*-
"""
ملف الإعدادات الرئيسية للتطبيق
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()

# المسارات الأساسية
BASE_DIR = Path(__file__).resolve().parent
ARCHIVE_DIR = BASE_DIR / "archive"
DATABASE_DIR = BASE_DIR / "database"
LOGS_DIR = BASE_DIR / "logs"
RESOURCES_DIR = BASE_DIR / "resources"

# إنشاء المجلدات إذا لم تكن موجودة
for directory in [ARCHIVE_DIR, DATABASE_DIR, LOGS_DIR, RESOURCES_DIR]:
    directory.mkdir(exist_ok=True)

# إعدادات قاعدة البيانات
DATABASE_PATH = DATABASE_DIR / "documents.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# إعدادات الواجهة الرسومية
APP_NAME = "نظام التعرف الذكي على المستندات والأرشفة"
APP_VERSION = "1.0.0"
APP_AUTHOR = "Almoon866"
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900
WINDOW_TITLE = f"{APP_NAME} v{APP_VERSION}"

# إعدادات اللغة والترجمة
DEFAULT_LANGUAGE = "ar"
SUPPORTED_LANGUAGES = ["ar", "en"]

# إعدادات OCR
OCR_LANGUAGE = "ar"
OCR_USE_GPU = False
OCR_SHOW_LOG = False
OCR_USE_ANGLE_CLS = True

# إعدادات الذكاء الاصطناعي
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2:7b")
OLLAMA_TIMEOUT = 300  # ثانية

# إعدادات معالجة الملفات
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500 MB
SUPPORTED_FILE_TYPES = {
    'application/pdf': '.pdf',
    'application/msword': '.doc',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
    'application/vnd.ms-excel': '.xls',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '.xlsx',
    'application/vnd.ms-powerpoint': '.ppt',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation': '.pptx',
    'image/jpeg': '.jpg',
    'image/png': '.png',
    'image/tiff': '.tiff',
    'image/bmp': '.bmp',
    'text/plain': '.txt',
    'text/rtf': '.rtf',
}

# التصنيفات الافتراضية
DEFAULT_CATEGORIES = [
    "عقود ووثائق قانونية",
    "فواتير ومالية",
    "شهادات ومؤهلات",
    "خطابات ومراسلات",
    "تقارير",
    "هويات ووثائق شخصية",
    "صور ووسائط",
    "أخرى"
]

# إعدادات البحث
MAX_SEARCH_RESULTS = 100
SEARCH_INDEX_DIR = DATABASE_DIR / "search_index"
SEARCH_INDEX_DIR.mkdir(exist_ok=True)

# إعدادات السجلات
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = LOGS_DIR / "app.log"

# إعدادات النسخ الاحتياطي
BACKUP_DIR = DATABASE_DIR / "backups"
BACKUP_DIR.mkdir(exist_ok=True)
AUTO_BACKUP_ENABLED = True
BACKUP_INTERVAL = 3600  # ثانية (ساعة واحدة)

# إعدادات الأداء
THREAD_POOL_SIZE = 4
MAX_CONCURRENT_TASKS = 2

# إعدادات التطوير
DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"
TESTING_MODE = os.getenv("TESTING_MODE", "False").lower() == "true"
