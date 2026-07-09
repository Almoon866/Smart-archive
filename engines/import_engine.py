# -*- coding: utf-8 -*-
"""
محرك الاستيراد والتحقق - استقبال الملفات والتحقق من سلامتها
"""

import os
import hashlib
import logging
from pathlib import Path
from typing import Dict, Optional, Tuple

try:
    import magic
except ImportError:
    magic = None

logger = logging.getLogger(__name__)


class ImportEngine:
    """محرك استيراد وتحقق من الملفات"""

    # أنواع الملفات المدعومة
    SUPPORTED_MIMETYPES = {
        'application/pdf': 'PDF',
        'application/msword': 'Word',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'Word',
        'application/vnd.ms-excel': 'Excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'Excel',
        'application/vnd.ms-powerpoint': 'PowerPoint',
        'application/vnd.openxmlformats-officedocument.presentationml.presentation': 'PowerPoint',
        'image/jpeg': 'Image',
        'image/png': 'Image',
        'image/tiff': 'Image',
        'image/bmp': 'Image',
        'text/plain': 'Text',
        'text/rtf': 'RTF',
    }

    def __init__(self, max_file_size: int = 500 * 1024 * 1024):
        """
        تهيئة محرك الاستيراد
        
        Args:
            max_file_size: الحد الأقصى لحجم الملف بالبايت
        """
        self.max_file_size = max_file_size
        self.import_errors = []

    def detect_file_type(self, file_path: str) -> Optional[str]:
        """
        اكتشاف نوع الملف الحقيقي باستخدام python-magic
        
        Args:
            file_path: مسار الملف
            
        Returns:
            نوع الملف MIME أو None
        """
        try:
            if magic:
                mime_type = magic.from_file(file_path, mime=True)
                return mime_type
            else:
                # بديل: استخدام الامتداد
                ext = Path(file_path).suffix.lower()
                mime_map = {
                    '.pdf': 'application/pdf',
                    '.doc': 'application/msword',
                    '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                    '.xls': 'application/vnd.ms-excel',
                    '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    '.jpg': 'image/jpeg',
                    '.jpeg': 'image/jpeg',
                    '.png': 'image/png',
                    '.txt': 'text/plain',
                }
                return mime_map.get(ext, 'unknown')
        except Exception as e:
            logger.error(f"خطأ في اكتشاف نوع الملف: {str(e)}")
            return None

    def calculate_file_hash(self, file_path: str, algorithm: str = 'sha256') -> Optional[str]:
        """
        حساب بصمة الملف الرقمية
        
        Args:
            file_path: مسار الملف
            algorithm: خوارزمية التجزئة (md5, sha256, etc.)
            
        Returns:
            البصمة الرقمية للملف
        """
        try:
            hasher = hashlib.new(algorithm)
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception as e:
            logger.error(f"خطأ في حساب بصمة الملف: {str(e)}")
            return None

    def verify_file_integrity(self, file_path: str) -> Tuple[bool, str]:
        """
        التحقق من سلامة الملف
        
        Args:
            file_path: مسار الملف
            
        Returns:
            (صحيح/خاطئ، رسالة)
        """
        errors = []

        # التحقق من وجود الملف
        if not os.path.exists(file_path):
            return False, "الملف غير موجود"

        # التحقق من أن الملف ليس مجلد
        if not os.path.isfile(file_path):
            return False, "المسار ليس ملف"

        # التحقق من أن الملف قابل للقراءة
        if not os.access(file_path, os.R_OK):
            return False, "الملف غير قابل للقراءة"

        # التحقق من حجم الملف
        file_size = os.path.getsize(file_path)
        if file_size == 0:
            errors.append("الملف فارغ")
        if file_size > self.max_file_size:
            errors.append(f"حجم الملف يتجاوز الحد الأقصى ({self.max_file_size / 1024 / 1024:.1f} MB)")

        if errors:
            return False, " | ".join(errors)

        return True, "الملف سليم"

    def import_file(self, file_path: str) -> Dict:
        """
        استيراد الملف والتحقق من سلامته
        
        Args:
            file_path: مسار الملف
            
        Returns:
            قاموس بمعلومات الملف
        """
        result = {
            'success': False,
            'file_path': file_path,
            'filename': None,
            'file_size': None,
            'file_type': None,
            'mime_type': None,
            'file_hash': None,
            'is_supported': False,
            'integrity_status': None,
            'error': None
        }

        try:
            # التحقق من سلامة الملف
            is_valid, message = self.verify_file_integrity(file_path)
            result['integrity_status'] = message

            if not is_valid:
                result['error'] = message
                logger.error(f"فشل التحقق من الملف: {message}")
                return result

            # الحصول على معلومات الملف
            file_obj = Path(file_path)
            result['filename'] = file_obj.name
            result['file_size'] = os.path.getsize(file_path)

            # اكتشاف نوع الملف
            mime_type = self.detect_file_type(file_path)
            result['mime_type'] = mime_type
            result['file_type'] = self.SUPPORTED_MIMETYPES.get(mime_type, 'Unknown')
            result['is_supported'] = mime_type in self.SUPPORTED_MIMETYPES

            # حساب البصمة الرقمية
            file_hash = self.calculate_file_hash(file_path)
            result['file_hash'] = file_hash

            result['success'] = True
            logger.info(f"تم استيراد الملف بنجاح: {result['filename']}")

        except Exception as e:
            result['error'] = f"خطأ غير متوقع: {str(e)}"
            logger.error(result['error'])

        return result
