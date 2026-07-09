# -*- coding: utf-8 -*-
"""
نظام السجلات للتطبيق
"""

import logging
import logging.handlers
from pathlib import Path
import config


def setup_logger(name: str) -> logging.Logger:
    """
    إعداد نظام السجلات
    
    Args:
        name: اسم المسجل (عادة __name__)
        
    Returns:
        كائن المسجل
    """
    logger = logging.getLogger(name)
    
    # تعيين مستوى السجل
    log_level = getattr(logging, config.LOG_LEVEL, logging.INFO)
    logger.setLevel(log_level)
    
    # تنسيق السجل
    formatter = logging.Formatter(config.LOG_FORMAT)
    
    # معالج الملف (يحفظ السجلات في ملف)
    file_handler = logging.handlers.RotatingFileHandler(
        filename=config.LOG_FILE,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # معالج الكونسول (يعرض السجلات في الشاشة)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger
