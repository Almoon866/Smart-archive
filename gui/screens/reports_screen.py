# -*- coding: utf-8 -*-
"""
شاشة التقارير والإحصائيات
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtGui import QFont
from database.db_manager import DatabaseManager
import logging

logger = logging.getLogger(__name__)


class ReportsScreen(QWidget):
    """
    شاشة التقارير والإحصائيات
    """

    def __init__(self, db: DatabaseManager):
        """
        تهيئة شاشة التقارير
        
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
        title = QLabel("التقارير والإحصائيات")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # محتوى التقارير
        content = QLabel(
            "سيتم عرض التقارير والرسوم البيانية هنا:\n\n"
            "• توزيع المستندات حسب النوع\n"
            "• توزيع المستندات حسب التصنيف\n"
            "• الإحصائيات الشهرية\n"
            "• أكثر الأشخاص ارتباطاً\n"
            "• مساحة التخزين"
        )
        layout.addWidget(content)
        layout.addStretch()

    def refresh_data(self):
        """
        تحديث بيانات التقارير
        """
        stats = self.db.get_statistics()
        logger.info(f"تم تحديث التقارير: {stats}")
