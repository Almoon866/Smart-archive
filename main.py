# -*- coding: utf-8 -*-
"""
نقطة البداية الرئيسية للتطبيق
"""

import sys
import logging
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon, QFont
from PyQt6.QtCore import Qt

# استيراد الإعدادات والمكونات
import config
from utils.logger import setup_logger
from gui.main_window import MainWindow
from database.db_manager import DatabaseManager

# إعداد السجلات
logger = setup_logger(__name__)


def initialize_application():
    """
    تهيئة التطبيق والمكونات الأساسية
    """
    try:
        # تهيئة قاعدة البيانات
        logger.info("جاري تهيئة قاعدة البيانات...")
        db = DatabaseManager(str(config.DATABASE_PATH))
        db.initialize_database()
        logger.info("تم تهيئة قاعدة البيانات بنجاح")

        return db

    except Exception as e:
        logger.error(f"خطأ في تهيئة التطبيق: {str(e)}")
        raise


def main():
    """
    الدالة الرئيسية لتشغيل التطبيق
    """
    try:
        logger.info(f"جاري بدء {config.APP_NAME} v{config.APP_VERSION}")
        logger.info(f"وضع التصحيح: {config.DEBUG_MODE}")

        # إنشاء تطبيق PyQt6
        app = QApplication(sys.argv)
        app.setApplicationName(config.APP_NAME)
        app.setApplicationVersion(config.APP_VERSION)

        # تعيين الخط الافتراضي
        font = QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        app.setFont(font)

        # تهيئة التطبيق
        db = initialize_application()

        # إنشاء النافذة الرئيسية
        logger.info("جاري إنشاء واجهة المستخدم...")
        main_window = MainWindow(db)
        main_window.show()

        logger.info(f"{config.APP_NAME} جاهزة للاستخدام")

        # تشغيل حلقة الأحداث
        sys.exit(app.exec())

    except Exception as e:
        logger.critical(f"خطأ حرج: {str(e)}")
        print(f"❌ خطأ حرج: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
