#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
اختبار سريع للتطبيق
"""

import sys
import logging
from pathlib import Path

# إعداد السجلات
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_imports():
    """
    اختبار استيراد المكتبات
    """
    print("\n🧪 اختبار الاستيرادات...")
    print("=" * 50)
    
    tests = [
        ("PyQt6", lambda: __import__('PyQt6')),
        ("PyMuPDF", lambda: __import__('fitz')),
        ("python-docx", lambda: __import__('docx')),
        ("openpyxl", lambda: __import__('openpyxl')),
        ("Pillow", lambda: __import__('PIL')),
        ("opencv", lambda: __import__('cv2')),
        ("paddleocr", lambda: __import__('paddleocr')),
        ("langdetect", lambda: __import__('langdetect')),
        ("requests", lambda: __import__('requests')),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            test_func()
            print(f"✅ {name}")
            passed += 1
        except ImportError as e:
            print(f"❌ {name}: {str(e)}")
            failed += 1
    
    print(f"\n📊 النتيجة: {passed} نجح، {failed} فشل")
    return failed == 0


def test_engines():
    """
    اختبار المحركات
    """
    print("\n🔧 اختبار المحركات...")
    print("=" * 50)
    
    try:
        from engines.import_engine import ImportEngine
        print("✅ ImportEngine")
        
        from engines.extraction_engine import ExtractionEngine
        print("✅ ExtractionEngine")
        
        from engines.ocr_engine import OCREngine
        print("✅ OCREngine")
        
        from engines.naming_engine import NamingEngine
        print("✅ NamingEngine")
        
        from engines.classification_engine import ClassificationEngine
        print("✅ ClassificationEngine")
        
        from engines.archive_engine import ArchiveEngine
        print("✅ ArchiveEngine")
        
        from engines.search_engine import SearchEngine
        print("✅ SearchEngine")
        
        return True
    except Exception as e:
        print(f"❌ خطأ في تحميل المحركات: {e}")
        return False


def test_database():
    """
    اختبار قاعدة البيانات
    """
    print("\n💾 اختبار قاعدة البيانات...")
    print("=" * 50)
    
    try:
        from database.db_manager import DatabaseManager
        import config
        
        db = DatabaseManager(str(config.DATABASE_PATH))
        print("✅ اتصال قاعدة البيانات")
        
        db.initialize_database()
        print("✅ تهيئة قاعدة البيانات")
        
        stats = db.get_statistics()
        print(f"✅ الإحصائيات: {stats}")
        
        db.close()
        return True
    except Exception as e:
        print(f"❌ خطأ في قاعدة البيانات: {e}")
        return False


def test_gui():
    """
    اختبار واجهة المستخدم
    """
    print("\n🖥️ اختبار واجهة المستخدم...")
    print("=" * 50)
    
    try:
        from gui.main_window import MainWindow
        print("✅ MainWindow")
        
        from gui.screens.dashboard_screen import DashboardScreen
        print("✅ DashboardScreen")
        
        from gui.screens.import_screen import ImportScreen
        print("✅ ImportScreen")
        
        from gui.screens.manager_screen import ManagerScreen
        print("✅ ManagerScreen")
        
        from gui.screens.search_screen import SearchScreen
        print("✅ SearchScreen")
        
        from gui.screens.reports_screen import ReportsScreen
        print("✅ ReportsScreen")
        
        from gui.screens.settings_screen import SettingsScreen
        print("✅ SettingsScreen")
        
        return True
    except Exception as e:
        print(f"❌ خطأ في واجهة المستخدم: {e}")
        return False


def test_utils():
    """
    اختبار الأدوات المساعدة
    """
    print("\n🛠️ اختبار الأدوات...")
    print("=" * 50)
    
    try:
        from utils.logger import setup_logger
        logger = setup_logger(__name__)
        print("✅ Logger")
        
        from utils.file_utils import sanitize_filename
        result = sanitize_filename("test<file>.pdf")
        assert result == "test-file.pdf"
        print("✅ file_utils")
        
        from utils.text_utils import clean_text
        result = clean_text("  hello  world  ")
        assert result == "hello world"
        print("✅ text_utils")
        
        return True
    except Exception as e:
        print(f"❌ خطأ في الأدوات: {e}")
        return False


def check_directories():
    """
    التحقق من المجلدات المطلوبة
    """
    print("\n📁 التحقق من المجلدات...")
    print("=" * 50)
    
    directories = [
        'archive',
        'database',
        'logs',
    ]
    
    for directory in directories:
        path = Path(directory)
        if path.exists():
            print(f"✅ {directory}")
        else:
            print(f"⚠️ {directory} - سيتم إنشاؤه")
            path.mkdir(parents=True, exist_ok=True)
    
    return True


def main():
    """
    تشغيل جميع الاختبارات
    """
    print("\n" + "*" * 60)
    print("* نظام التعرف الذكي على المستندات")
    print("* اختبار شامل للتطبيق")
    print("*" * 60)
    
    results = []
    
    # الاختبارات
    results.append(("الاستيرادات", test_imports()))
    results.append(("المحركات", test_engines()))
    results.append(("قاعدة البيانات", test_database()))
    results.append(("واجهة المستخدم", test_gui()))
    results.append(("الأدوات", test_utils()))
    results.append(("المجلدات", check_directories()))
    
    # الملخص
    print("\n" + "=" * 50)
    print("📋 ملخص الاختبارات")
    print("=" * 50)
    
    for name, result in results:
        status = "✅ نجح" if result else "❌ فشل"
        print(f"{name}: {status}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\n📊 النتيجة الإجمالية: {passed}/{total} نجح")
    
    if passed == total:
        print("\n🎉 كل الاختبارات نجحت! يمكنك الآن تشغيل: python main.py")
    else:
        print(f"\n⚠️ {total - passed} اختبارات فشلت. يرجى التحقق.")
    
    print("\n" + "*" * 60 + "\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ خطأ حرج: {e}")
        sys.exit(1)
