# -*- coding: utf-8 -*-
"""
شاشة الإعدادات
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QGroupBox, QMessageBox
)
from PyQt6.QtGui import QFont
from database.db_manager import DatabaseManager
import logging
import config

logger = logging.getLogger(__name__)


class SettingsScreen(QWidget):
    """
    شاشة الإعدادات
    """

    def __init__(self, db: DatabaseManager):
        """
        تهيئة شاشة الإعدادات
        
        Args:
            db: مدير قاعدة البيانات
        """
        super().__init__()
        self.db = db
        self.init_ui()

    def init_ui(self):
        """
        إنشاء عناصر الشاشة
        """
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # العنوان
        title = QLabel("الإعدادات")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # مجموعة إعدادات الأرشفة
        archive_group = QGroupBox("إعدادات الأرشفة")
        archive_layout = QVBoxLayout()
        
        archive_label = QLabel(f"مسار الأرشفة: {config.ARCHIVE_DIR}")
        archive_layout.addWidget(archive_label)
        
        archive_group.setLayout(archive_layout)
        layout.addWidget(archive_group)
        
        # مجموعة إعدادات الذكاء الاصطناعي
        ai_group = QGroupBox("إعدادات الذكاء الاصطناعي")
        ai_layout = QVBoxLayout()
        
        ai_label = QLabel(f"خادم Ollama: {config.OLLAMA_BASE_URL}")
        ai_layout.addWidget(ai_label)
        
        model_label = QLabel(f"النموذج: {config.OLLAMA_MODEL}")
        ai_layout.addWidget(model_label)
        
        ai_group.setLayout(ai_layout)
        layout.addWidget(ai_group)
        
        # مجموعة الإجراءات
        actions_group = QGroupBox("الإجراءات")
        actions_layout = QVBoxLayout()
        
        backup_btn = QPushButton("💾 نسخة احتياطية")
        backup_btn.clicked.connect(self.create_backup)
        actions_layout.addWidget(backup_btn)
        
        clear_btn = QPushButton("🗑️ مسح سجلات النشاط")
        clear_btn.clicked.connect(self.clear_logs)
        actions_layout.addWidget(clear_btn)
        
        actions_group.setLayout(actions_layout)
        layout.addWidget(actions_group)
        
        layout.addStretch()

    def create_backup(self):
        """
        إنشاء نسخة احتياطية
        """
        QMessageBox.information(
            self,
            "نسخة احتياطية",
            "سيتم إضافة خاصية النسخ الاحتياطي قريباً"
        )

    def clear_logs(self):
        """
        مسح سجلات النشاط
        """
        reply = QMessageBox.question(
            self,
            "تأكيد",
            "هل تريد مسح سجلات النشاط بشكل نهائي؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            QMessageBox.information(self, "نجاح", "تم مسح السجلات")
