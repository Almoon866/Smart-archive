# -*- coding: utf-8 -*-
"""
شاشة لوحة التحكم
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout, QFrame
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor
from database.db_manager import DatabaseManager
import logging

logger = logging.getLogger(__name__)


class DashboardScreen(QWidget):
    """
    شاشة لوحة التحكم - عرض الإحصائيات السريعة
    """

    def __init__(self, db: DatabaseManager):
        """
        تهيئة شاشة لوحة التحكم
        
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
        title = QLabel("لوحة التحكم")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # شبكة الإحصائيات
        stats_layout = QGridLayout()
        
        # الإحصائيات
        stats = self.db.get_statistics()
        
        # بطاقة العدد الإجمالي للمستندات
        total_docs = QFrame()
        total_docs.setStyleSheet("""
            QFrame {
                background-color: #3498db;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        total_layout = QVBoxLayout(total_docs)
        total_label = QLabel("إجمالي المستندات")
        total_label.setStyleSheet("color: white; font-weight: bold;")
        total_count = QLabel(str(stats.get('total_documents', 0)))
        total_count.setStyleSheet("color: white; font-size: 28px; font-weight: bold;")
        total_layout.addWidget(total_label)
        total_layout.addWidget(total_count)
        stats_layout.addWidget(total_docs, 0, 0)
        
        # بطاقة المستندات المعتمدة
        approved_docs = QFrame()
        approved_docs.setStyleSheet("""
            QFrame {
                background-color: #2ecc71;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        approved_layout = QVBoxLayout(approved_docs)
        approved_label = QLabel("مستندات معتمدة")
        approved_label.setStyleSheet("color: white; font-weight: bold;")
        approved_count = QLabel(str(stats.get('approved_documents', 0)))
        approved_count.setStyleSheet("color: white; font-size: 28px; font-weight: bold;")
        approved_layout.addWidget(approved_label)
        approved_layout.addWidget(approved_count)
        stats_layout.addWidget(approved_docs, 0, 1)
        
        # بطاقة حجم التخزين
        size_docs = QFrame()
        size_docs.setStyleSheet("""
            QFrame {
                background-color: #e74c3c;
                border-radius: 8px;
                padding: 20px;
            }
        """)
        size_layout = QVBoxLayout(size_docs)
        size_label = QLabel("حجم التخزين المستخدم")
        size_label.setStyleSheet("color: white; font-weight: bold;")
        total_size = stats.get('total_size', 0)
        size_mb = total_size / (1024 * 1024)
        size_count = QLabel(f"{size_mb:.2f} MB")
        size_count.setStyleSheet("color: white; font-size: 28px; font-weight: bold;")
        size_layout.addWidget(size_label)
        size_layout.addWidget(size_count)
        stats_layout.addWidget(size_docs, 0, 2)
        
        layout.addLayout(stats_layout)
        
        # معلومات إضافية
        info_label = QLabel("توزيع المستندات حسب التصنيف:")
        info_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(info_label)
        
        # عرض التصنيفات
        categories_layout = QVBoxLayout()
        for category, count in stats.get('documents_by_category', {}).items():
            cat_label = QLabel(f"• {category}: {count} مستند")
            categories_layout.addWidget(cat_label)
        
        layout.addLayout(categories_layout)
        layout.addStretch()
