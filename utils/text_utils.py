# -*- coding: utf-8 -*-
"""
أدوات معالجة النصوص
"""

import re
from typing import List, Dict


def clean_text(text: str) -> str:
    """
    تنظيف النص من المسافات الزائدة والرموز الغريبة
    
    Args:
        text: النص الخام
        
    Returns:
        النص المنظف
    """
    if not text:
        return ""
    
    # إزالة المسافات الزائدة
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    
    # إزالة الأحرف الغريبة
    text = text.replace('\x00', '')
    text = text.replace('\ufeff', '')  # BOM
    
    return text


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    اختصار النص إذا كان طويلاً جداً
    
    Args:
        text: النص
        max_length: الحد الأقصى للطول
        suffix: اللاحقة (نقاط)
        
    Returns:
        النص المختصر
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def extract_words(text: str, min_length: int = 3) -> List[str]:
    """
    استخراج الكلمات من النص
    
    Args:
        text: النص
        min_length: الحد الأدنى لطول الكلمة
        
    Returns:
        قائمة الكلمات
    """
    # دعم النصوص العربية والإنجليزية
    words = re.findall(r'[\u0600-\u06FF\w]+', text)
    return [w for w in words if len(w) >= min_length]


def highlight_text(text: str, keywords: List[str]) -> str:
    """
    إضافة تعليمات HTML لتمييز الكلمات المهمة
    
    Args:
        text: النص
        keywords: الكلمات المراد تمييزها
        
    Returns:
        النص مع التعليمات
    """
    for keyword in keywords:
        # استبدال الكلمة مع الحفاظ على الحالة
        pattern = re.compile(re.escape(keyword), re.IGNORECASE)
        text = pattern.sub(f'<mark>{keyword}</mark>', text)
    
    return text
