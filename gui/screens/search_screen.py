# -*- coding: utf-8 -*-
"""
شاشة البحث المتقدم
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from database.db_manager import DatabaseManager
import logging

logger = logging.getLogger(__name__)


class SearchScreen(QWidget):
    """
    شاشة البحث المتقدم
    """

    def __init__(self, db: DatabaseManager):
        """
        تهيئة شاشة البحث
        
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
        title = QLabel("البحث المتقدم")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # منطقة البحث
        search_layout = QHBoxLayout()
        
        search_label = QLabel("ابحث عن:")
        search_layout.addWidget(search_label)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("أدخل نص البحث...")
        self.search_input.textChanged.connect(self.on_search_text_changed)
        search_layout.addWidget(self.search_input)
        
        search_btn = QPushButton("🔍 بحث")
        search_btn.clicked.connect(self.perform_search)
        search_layout.addWidget(search_btn)
        
        layout.addLayout(search_layout)
        
        # جدول النتائج
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(6)
        self.results_table.setHorizontalHeaderLabels([
            "الاسم الذكي",
            "النوع",
            "التصنيف",
            "المسؤول",
            "التاريخ",
            "الثقة"
        ])
        layout.addWidget(self.results_table)

    def on_search_text_changed(self, text: str):
        """
        معالج تغيير نص البحث
        
        Args:
            text: النص المدخل
        """
        if len(text) >= 2:
            self.perform_search()

    def perform_search(self):
        """
        تنفيذ البحث
        """
        query = self.search_input.text().strip()
        
        if not query:
            self.results_table.setRowCount(0)
            return
        
        results = self.db.search_documents(query)
        
        self.results_table.setRowCount(0)
        for doc in results:
            row = self.results_table.rowCount()
            self.results_table.insertRow(row)
            
            self.results_table.setItem(row, 0, QTableWidgetItem(doc.get('smart_name', '-')))
            self.results_table.setItem(row, 1, QTableWidgetItem(doc.get('document_type', '-')))
            self.results_table.setItem(row, 2, QTableWidgetItem(doc.get('category', '-')))
            self.results_table.setItem(row, 3, QTableWidgetItem(doc.get('responsible_person', '-')))
            self.results_table.setItem(row, 4, QTableWidgetItem(str(doc.get('created_at', '-'))[:10]))
            self.results_table.setItem(row, 5, QTableWidgetItem(f"{doc.get('confidence', 0):.0%}"))
