# -*- coding: utf-8 -*-
"""
محرك OCR - تحويل الصور والمسح الضوئي إلى نص
"""

import logging
from typing import Dict, Optional
import cv2
import numpy as np

try:
    from paddleocr import PaddleOCR
except ImportError:
    PaddleOCR = None

logger = logging.getLogger(__name__)


class OCREngine:
    """محرك OCR للنصوص العربية"""

    def __init__(self, use_gpu: bool = False):
        """
        تهيئة محرك OCR
        
        Args:
            use_gpu: استخدام GPU (إن أمكن)
        """
        self.use_gpu = use_gpu
        self.ocr = None
        self._initialize_paddle_ocr()

    def _initialize_paddle_ocr(self):
        """
        تهيئة PaddleOCR للعربية
        """
        try:
            if PaddleOCR:
                logger.info("جاري تهيئة PaddleOCR للغة العربية...")
                self.ocr = PaddleOCR(
                    use_angle_cls=True,
                    lang='ar',
                    use_gpu=self.use_gpu,
                    show_log=False
                )
                logger.info("تم تهيئة PaddleOCR بنجاح")
            else:
                logger.warning("مكتبة PaddleOCR غير مثبتة")
        except Exception as e:
            logger.error(f"خطأ في تهيئة PaddleOCR: {str(e)}")
            self.ocr = None

    def enhance_image_quality(self, image_path: str) -> Optional[np.ndarray]:
        """
        تحسين جودة الصورة للحصول على OCR أفضل
        
        Args:
            image_path: مسار الصورة
            
        Returns:
            الصورة المحسّنة
        """
        try:
            img = cv2.imread(image_path)
            if img is None:
                logger.error(f"لا يمكن قراءة الصورة: {image_path}")
                return None

            # تحويل إلى رمادي
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # تحسين التباين (CLAHE - Contrast Limited Adaptive Histogram Equalization)
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(gray)

            # إزالة الضوضاء
            denoised = cv2.fastNlMeansDenoising(
                enhanced,
                h=10,
                templateWindowSize=7,
                searchWindowSize=21
            )

            # تصحيح الميل (skew correction) - اختياري
            # يمكن إضافة هنا لاحقاً إذا لزم الأمر

            return denoised

        except Exception as e:
            logger.error(f"خطأ في تحسين جودة الصورة: {str(e)}")
            return None

    def extract_text_from_image(self, image_path: str) -> Dict:
        """
        استخراج النص من صورة باستخدام OCR
        
        Args:
            image_path: مسار الصورة
            
        Returns:
            قاموس بالنص والثقة والمعلومات الأخرى
        """
        result = {
            'success': False,
            'text': '',
            'raw_text': '',
            'confidence': 0.0,
            'details': [],
            'error': None
        }

        try:
            if not self.ocr:
                result['error'] = "محرك OCR لم يتم تهيئته"
                logger.error(result['error'])
                return result

            # تحسين جودة الصورة
            enhanced_img = self.enhance_image_quality(image_path)
            if enhanced_img is None:
                result['error'] = "فشل تحسين جودة الصورة"
                return result

            # تطبيق OCR
            logger.info(f"جاري تطبيق OCR على الصورة: {image_path}")
            ocr_result = self.ocr.ocr(enhanced_img, cls=True)

            if not ocr_result or len(ocr_result) == 0:
                result['error'] = "فشل استخراج النص من الصورة"
                logger.warning(result['error'])
                return result

            # معالجة النتائج
            extracted_lines = []
            total_confidence = 0
            line_count = 0

            for page in ocr_result:
                for line in page:
                    text = line[1]
                    confidence = line[2]

                    extracted_lines.append(text)
                    total_confidence += confidence
                    line_count += 1

                    result['details'].append({
                        'text': text,
                        'confidence': confidence
                    })

            # دمج النصوص
            result['raw_text'] = ' '.join(extracted_lines)
            result['text'] = self._post_process_text(result['raw_text'])
            
            # حساب متوسط الثقة
            result['confidence'] = total_confidence / line_count if line_count > 0 else 0.0
            result['success'] = True

            logger.info(f"تم استخراج النص بنجاح (ثقة: {result['confidence']:.2%})")

        except Exception as e:
            result['error'] = f"خطأ في استخراج النص: {str(e)}"
            logger.error(result['error'])

        return result

    def _post_process_text(self, text: str) -> str:
        """
        معالجة لاحقة للنص المستخرج من OCR
        
        Args:
            text: النص الخام من OCR
            
        Returns:
            النص المعالج
        """
        import re

        # إزالة المسافات الزائدة
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\s+([.,،؛])', r'\1', text)

        # تصحيح بعض الأخطاء الشائعة في OCR العربي
        corrections = {
            'ا\\': 'ا',
            '\\ا': 'ا',
            'ي ': 'ي',
            'ق ': 'ق',
        }
        for wrong, correct in corrections.items():
            text = text.replace(wrong, correct)

        return text.strip()
