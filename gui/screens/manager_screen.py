# -*- coding: utf-8 -*-
"""
شاشة إدارة الملفات
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget,
    QTableWidgetItem, QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from database.db_manager import DatabaseManager
import logging

logger = logging.getLogger(__name__)


class ManagerScreen(QWidget):
    """
    شاشة إدارة الملفات المؤرشفة
    """

    def __init__(self, db: DatabaseManager):
        """
        تهيئة شاشة الإدارة
        
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
        title = QLabel("إدارة المستندات")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # جدول المستندات
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "الاسم الذكي",
            "نوع المستند",
            "التصنيف",
            "المسؤول",
            "الحجم",
            "التاريخ",
            "الثقة",
            "إجراءات"
        ])
        self.table.setColumnWidth(0, 200)
        self.table.setColumnWidth(1, 100)
        self.table.setColumnWidth(2, 100)
        self.table.setColumnWidth(3, 100)
        layout.addWidget(self.table)
        
        # أزرار التحكم
        button_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("🔄 تحديث")
        refresh_btn.clicked.connect(self.refresh_data)
        button_layout.addWidget(refresh_btn)
        
        delete_btn = QPushButton("🗑️ حذف")
        delete_btn.clicked.connect(self.delete_selected)
        button_layout.addWidget(delete_btn)
        
        export_btn = QPushButton("📤 تصدير")
        export_btn.clicked.connect(self.export_data)
        button_layout.addWidget(export_btn)
        
        layout.addLayout(button_layout)

    def refresh_data(self):
        """
        تحديث بيانات الجدول
        """
        documents = self.db.get_all_documents(limit=1000)
        self.table.setRowCount(0)
        
        for doc in documents:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            self.table.setItem(row, 0, QTableWidgetItem(doc.get('smart_name', '-')))
            self.table.setItem(row, 1, QTableWidgetItem(doc.get('document_type', '-')))
            self.table.setItem(row, 2, QTableWidgetItem(doc.get('category', '-')))
            self.table.setItem(row, 3, QTableWidgetItem(doc.get('responsible_person', '-')))
            
            size_mb = doc.get('file_size', 0) / (1024 * 1024)
            self.table.setItem(row, 4, QTableWidgetItem(f"{size_mb:.2f} MB"))
            self.table.setItem(row, 5, QTableWidgetItem(str(doc.get('created_at', '-'))[:10]))
            self.table.setItem(row, 6, QTableWidgetItem(f"{doc.get('confidence', 0):.0%}"))
            
            # زر الحذف
            delete_btn = QPushButton("🗑️")
            delete_btn.clicked.connect(lambda checked, doc_id=doc['id']: self.delete_document(doc_id))
            self.table.setCellWidget(row, 7, delete_btn)

    def delete_selected(self):
        """
        حذف الصف المحدد
        """
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "تنبيه", "اختر صفاً للحذف")
            return
        
        # استخراج معرف المستند من الصف
        # يمكن تحسين هذا بحفظ المعرف في بيانات الصف
        reply = QMessageBox.question(
            self,
            "تأكيد",
            "هل تريد حذف هذا المستند؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.table.removeRow(current_row)

    def delete_document(self, doc_id: int):
        """
        حذف مستند
        
        Args:
            doc_id: معرف المستند
        """
        reply = QMessageBox.question(
            self,
            "تأكيد الحذف",
            "هل تريد حذف هذا المستند نهائياً؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.db.delete_document(doc_id):
                QMessageBox.information(self, "نجاح", "تم حذف المستند بنجاح")
                self.refresh_data()
            else:
                QMessageBox.critical(self, "خطأ", "فشل حذف المستند")

    def export_data(self):
        """
        تصدير البيانات
        """
        QMessageBox.information(
            self,
            "تصدير",
            "سيتم إضافة خاصية التصدير إلى Excel/PDF قريباً"
        )
