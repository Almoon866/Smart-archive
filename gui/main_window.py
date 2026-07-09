# -*- coding: utf-8 -*-
"""
النافذة الرئيسية للتطبيق
"""

import sys
import logging
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget,
    QPushButton, QLabel, QToolBar, QStatusBar, QMessageBox
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QFont, QColor

import config
from database.db_manager import DatabaseManager
from gui.screens.dashboard_screen import DashboardScreen
from gui.screens.import_screen import ImportScreen
from gui.screens.manager_screen import ManagerScreen
from gui.screens.search_screen import SearchScreen
from gui.screens.reports_screen import ReportsScreen
from gui.screens.settings_screen import SettingsScreen

logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """
النافذة الرئيسية للتطبيق
    """

    def __init__(self, db: DatabaseManager):
        """
        تهيئة النافذة الرئيسية
        
        Args:
            db: مدير قاعدة البيانات
        """
        super().__init__()
        self.db = db
        self.setWindowTitle(config.WINDOW_TITLE)
        self.setGeometry(100, 100, config.WINDOW_WIDTH, config.WINDOW_HEIGHT)
        
        # تطبيق الأنماط
        self.apply_styles()
        
        # إنشاء الواجهة
        self.init_ui()
        
        logger.info("تم إنشاء النافذة الرئيسية بنجاح")

    def apply_styles(self):
        """
        تطبيق أنماط CSS على التطبيق
        """
        stylesheet = """
            QMainWindow {
                background-color: #f5f5f5;
            }
            QToolBar {
                background-color: #2c3e50;
                border-bottom: 2px solid #34495e;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1f618d;
            }
            QStatusBar {
                background-color: #ecf0f1;
                color: #2c3e50;
            }
            QLabel {
                color: #2c3e50;
            }
        """
        self.setStyleSheet(stylesheet)

    def init_ui(self):
        """
        إنشاء عناصر الواجهة
        """
        # إنشاء الأداة المركزية
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # إنشاء الشريط الجانبي
        self.sidebar = self.create_sidebar()
        main_layout.addWidget(self.sidebar)
        
        # إنشاء منطقة المحتوى
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget, 1)
        
        # إضافة الشاشات
        self.dashboard_screen = DashboardScreen(self.db)
        self.import_screen = ImportScreen(self.db)
        self.manager_screen = ManagerScreen(self.db)
        self.search_screen = SearchScreen(self.db)
        self.reports_screen = ReportsScreen(self.db)
        self.settings_screen = SettingsScreen(self.db)
        
        self.stacked_widget.addWidget(self.dashboard_screen)
        self.stacked_widget.addWidget(self.import_screen)
        self.stacked_widget.addWidget(self.manager_screen)
        self.stacked_widget.addWidget(self.search_screen)
        self.stacked_widget.addWidget(self.reports_screen)
        self.stacked_widget.addWidget(self.settings_screen)
        
        # شريط الحالة
        self.statusBar().showMessage("جاهز")
        
        # عرض الشاشة الأولى (لوحة التحكم)
        self.show_dashboard()

    def create_sidebar(self) -> QWidget:
        """
        إنشاء الشريط الجانبي بالأزرار
        
        Returns:
            القطعة (Widget) للشريط الجانبي
        """
        sidebar = QWidget()
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar.setMaximumWidth(200)
        sidebar.setStyleSheet("""
            QWidget {
                background-color: #2c3e50;
            }
            QPushButton {
                background-color: #2c3e50;
                color: white;
                border: none;
                padding: 12px;
                text-align: left;
                font-weight: bold;
                border-left: 4px solid transparent;
            }
            QPushButton:hover {
                background-color: #34495e;
                border-left: 4px solid #3498db;
            }
            QLabel {
                color: white;
                font-weight: bold;
                padding: 10px;
            }
        """)
        
        # العنوان
        title = QLabel("القوائم")
        title.setFont(QFont("Arial", 12))
        sidebar_layout.addWidget(title)
        
        # الأزرار
        buttons = [
            ("📊 لوحة التحكم", self.show_dashboard),
            ("📁 استيراد الملفات", self.show_import),
            ("📋 إدارة الملفات", self.show_manager),
            ("🔍 بحث متقدم", self.show_search),
            ("📈 التقارير", self.show_reports),
            ("⚙️ الإعدادات", self.show_settings),
        ]
        
        for text, callback in buttons:
            btn = QPushButton(text)
            btn.clicked.connect(callback)
            sidebar_layout.addWidget(btn)
        
        sidebar_layout.addStretch()
        
        # زر الخروج
        exit_btn = QPushButton("🚪 خروج")
        exit_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        exit_btn.clicked.connect(self.close_app)
        sidebar_layout.addWidget(exit_btn)
        
        return sidebar

    def show_dashboard(self):
        """عرض لوحة التحكم"""
        self.stacked_widget.setCurrentWidget(self.dashboard_screen)
        self.statusBar().showMessage("لوحة التحكم")

    def show_import(self):
        """عرض شاشة الاستيراد"""
        self.stacked_widget.setCurrentWidget(self.import_screen)
        self.statusBar().showMessage("استيراد الملفات")

    def show_manager(self):
        """عرض شاشة إدارة الملفات"""
        self.stacked_widget.setCurrentWidget(self.manager_screen)
        self.statusBar().showMessage("إدارة الملفات")
        self.manager_screen.refresh_data()

    def show_search(self):
        """عرض شاشة البحث"""
        self.stacked_widget.setCurrentWidget(self.search_screen)
        self.statusBar().showMessage("البحث المتقدم")

    def show_reports(self):
        """عرض شاشة التقارير"""
        self.stacked_widget.setCurrentWidget(self.reports_screen)
        self.statusBar().showMessage("التقارير والإحصائيات")
        self.reports_screen.refresh_data()

    def show_settings(self):
        """عرض شاشة الإعدادات"""
        self.stacked_widget.setCurrentWidget(self.settings_screen)
        self.statusBar().showMessage("الإعدادات")

    def close_app(self):
        """
        إغلاق التطبيق بشكل آمن
        """
        reply = QMessageBox.question(
            self,
            "تأكيد الخروج",
            "هل تريد فعلاً الخروج من التطبيق؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            logger.info("إغلاق التطبيق")
            self.db.close()
            sys.exit(0)

    def closeEvent(self, event):
        """
        معالج إغلاق النافذة
        
        Args:
            event: حدث الإغلاق
        """
        self.db.close()
        event.accept()
