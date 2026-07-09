# -*- coding: utf-8 -*-
"""
أدوات الملفات المساعدة
"""

import os
import re
from pathlib import Path
from typing import Tuple


def sanitize_filename(filename: str, replacement: str = "-") -> str:
    """
    تنظيف اسم الملف من الأحرف غير المسموحة
    
    Args:
        filename: اسم الملف
        replacement: الحرف البديل
        
    Returns:
        اسم الملف المنظف
    """
    # الأحرف غير المسموحة في أسماء الملفات
    invalid_chars = r'[<>:"/\\|?*]'
    sanitized = re.sub(invalid_chars, replacement, filename)
    
    # إزالة المسافات الزائدة
    sanitized = sanitized.strip()
    
    # التأكد من عدم ترك الاسم فارغاً
    if not sanitized or sanitized == replacement * len(sanitized):
        sanitized = "untitled"
    
    # الحد من طول الاسم
    max_length = 200
    if len(sanitized) > max_length:
        name, ext = os.path.splitext(sanitized)
        sanitized = name[:max_length - len(ext)] + ext
    
    return sanitized


def get_file_extension(filename: str) -> str:
    """
    الحصول على امتداد الملف
    
    Args:
        filename: اسم الملف
        
    Returns:
        الامتداد بدون النقطة
    """
    _, ext = os.path.splitext(filename)
    return ext.lstrip('.').lower()


def format_file_size(size_bytes: int) -> str:
    """
    تنسيق حجم الملف بصيغة قابلة للقراءة
    
    Args:
        size_bytes: حجم الملف بالبايتات
        
    Returns:
        حجم الملف المنسق (KB, MB, GB, etc.)
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"


def create_directory_structure(archive_dir: Path, category: str, year: str) -> Path:
    """
    إنشاء هيكل المجلدات للأرشفة
    
    Args:
        archive_dir: مجلد الأرشفة الرئيسي
        category: التصنيف
        year: السنة
        
    Returns:
        مسار المجلد المُنشأ
    """
    target_dir = archive_dir / category / year
    target_dir.mkdir(parents=True, exist_ok=True)
    return target_dir
