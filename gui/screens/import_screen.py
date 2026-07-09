# -*- coding: utf-8 -*-
"""
شاشة استيراد الملفات
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QProgressBar, QTextEdit, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QDropEvent, QDragEnterEvent
from database.db_manager import DatabaseManager
from engines.import_engine import ImportEngine
from engines.extraction_engine import ExtractionEngine
from engines.ocr_engine import OCREngine
from engines.naming_engine import NamingEngine
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class FileProcessorThread(QThread):
    """
    خيط منفصل لمعالجة الملفات
    """
    progress_updated = pyqtSignal(str)
    processing_complete = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, file_path: str):
        super().__init__()
        self.file_path = file_path

    def run(self):
        """
        معالجة الملف
        """
        try:
            # استيراد
            self.progress_updated.emit("جاري فحص الملف...")
            import_engine = ImportEngine()
            import_result = import_engine.import_file(self.file_path)
            
            if not import_result['success']:
                self.error_occurred.emit(f"خطأ في الاستيراد: {import_result['error']}")
                return
            
            # استخراج المحتوى
            self.progress_updated.emit("جاري استخراج المحتوى...")
            extraction_engine = ExtractionEngine()
            extraction_result = extraction_engine.extract_content(
                self.file_path,
                import_result['file_type']
            )
            
            if not extraction_result['success']:
                self.error_occurred.emit(f"خطأ في الاستخراج: {extraction_result['error']}")
                return
            
            text = extraction_result['text']
            
            # OCR إذا لزم الأمر
            if extraction_result.get('requires_ocr') and extraction_result['text'] == "[صورة - يتطلب معالجة OCR]":
                self.progress_updated.emit("جاري تطبيق OCR...")
                ocr_engine = OCREngine()
                ocr_result = ocr_engine.extract_text_from_image(self.file_path)
                if ocr_result['success']:
                    text = ocr_result['text']
            
            # التسمية الذكية
            self.progress_updated.emit("جاري استخراج الاسم الذكي...")
            naming_engine = NamingEngine()
            naming_result = naming_engine.generate_smart_name(
                text,
                import_result['filename']
            )
            
            if not naming_result['success']:
                self.error_occurred.emit(f"خطأ في التسمية الذكية: {naming_result['error']}")
                return
            
            result = {
                'import_result': import_result,
                'extraction_result': extraction_result,
                'naming_result': naming_result,
                'text': text
            }
            
            self.progress_updated.emit("اكتمل!")
            self.processing_complete.emit(result)
            
        except Exception as e:
            self.error_occurred.emit(f"خطأ غير متوقع: {str(e)}")
            logger.error(f"خطأ في معالجة الملف: {str(e)}")


class ImportScreen(QWidget):
    """
    شاشة استيراد الملفات
    """

    def __init__(self, db: DatabaseManager):
        """
        تهيئة شاشة الاستيراد
        
        Args:
            db: مدير قاعدة البيانات
        """
        super().__init__()
        self.db = db
        self.current_file = None
        self.processing_thread = None
        self.init_ui()
        self.setAcceptDrops(True)

    def init_ui(self):
        """
        إنشاء عناصر الشاشة
        """
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # العنوان
        title = QLabel("استيراد الملفات")
        title.setFont(QFont("Arial", 18, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # منطقة السحب والإفلات
        drop_area = QLabel(
            "اسحب الملفات هنا أو اضغط على الزر أدناه\n"
            "الملفات المدعومة: PDF, DOCX, XLSX, صور, نصوص"
        )
        drop_area.setStyleSheet("""
            QLabel {
                background-color: #ecf0f1;
                border: 2px dashed #3498db;
                border-radius: 8px;
                padding: 40px;
                text-align: center;
                color: #7f8c8d;
                font-weight: bold;
            }
        """)
        drop_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        drop_area.setMinimumHeight(150)
        self.drop_area = drop_area
        layout.addWidget(drop_area)
        
        # أزرار التحكم
        button_layout = QHBoxLayout()
        
        import_btn = QPushButton("📂 اختر ملف")
        import_btn.clicked.connect(self.choose_file)
        button_layout.addWidget(import_btn)
        
        clear_btn = QPushButton("🗑️ مسح")
        clear_btn.clicked.connect(self.clear_all)
        button_layout.addWidget(clear_btn)
        
        layout.addLayout(button_layout)
        
        # شريط التقدم
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # منطقة السجل
        log_label = QLabel("سجل المعالجة:")
        log_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(log_label)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)
        layout.addWidget(self.log_text)
        
        layout.addStretch()

    def choose_file(self):
        """
        فتح حوار اختيار الملف
        """
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setNameFilters((
            "جميع الملفات المدعومة (*.pdf *.docx *.doc *.xlsx *.jpg *.png *.txt)",
            "ملفات PDF (*.pdf)",
            "ملفات Word (*.docx *.doc)",
            "ملفات Excel (*.xlsx)",
            "صور (*.jpg *.jpeg *.png)",
            "نصوص (*.txt)",
        ))
        
        if file_dialog.exec() == QFileDialog.DialogCode.Accepted:
            file_path = file_dialog.selectedFiles()[0]
            self.process_file(file_path)

    def dragEnterEvent(self, event: QDragEnterEvent):
        """
        معالج دخول السحب
        
        Args:
            event: حدث السحب
        """
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        """
        معالج إفلات الملفات
        
        Args:
            event: حدث الإفلات
        """
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if Path(file_path).is_file():
                self.process_file(file_path)
                break  # معالجة ملف واحد فقط

    def process_file(self, file_path: str):
        """
        معالجة الملف
        
        Args:
            file_path: مسار الملف
        """
        self.current_file = file_path
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.log_text.clear()
        self.log_text.append(f"جاري معالجة: {Path(file_path).name}")
        
        self.processing_thread = FileProcessorThread(file_path)
        self.processing_thread.progress_updated.connect(self.on_progress_updated)
        self.processing_thread.processing_complete.connect(self.on_processing_complete)
        self.processing_thread.error_occurred.connect(self.on_error)
        self.processing_thread.start()

    def on_progress_updated(self, message: str):
        """
        تحديث رسالة التقدم
        
        Args:
            message: الرسالة
        """
        self.log_text.append(f"• {message}")

    def on_processing_complete(self, result: dict):
        """
        معالجة اكتمال المعالجة
        
        Args:
            result: نتائج المعالجة
        """
        self.progress_bar.setValue(100)
        naming_result = result['naming_result']
        
        message = (
            f"\n\n✅ معالجة ناجحة!\n\n"
            f"الاسم الذكي: {naming_result['smart_name']}\n"
            f"نوع المستند: {naming_result['document_type']}\n"
            f"التصنيف: {naming_result['category']}\n"
            f"المسؤول: {naming_result['responsible_person']}\n"
            f"الثقة: {naming_result['confidence']:.0%}"
        )
        self.log_text.append(message)
        
        QMessageBox.information(
            self,
            "نجاح",
            "تم معالجة الملف بنجاح!\n\n" + message
        )

    def on_error(self, error: str):
        """
        معالجة الأخطاء
        
        Args:
            error: رسالة الخطأ
        """
        self.progress_bar.setVisible(False)
        self.log_text.append(f"❌ خطأ: {error}")
        QMessageBox.critical(self, "خطأ", error)

    def clear_all(self):
        """
        مسح جميع البيانات
        """
        self.current_file = None
        self.log_text.clear()
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
