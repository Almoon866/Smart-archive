# -*- coding: utf-8 -*-
"""
محرك التسمية الذكية - استخراج أسماء بشرية ذكية للمستندات
هذا هو قلب النظام لاستخراج أسماء تشبه أسماء الإنسان العربي
"""

import re
import json
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import requests
from langdetect import detect, LangDetectException

logger = logging.getLogger(__name__)


class NamingEngine:
    """محرك التسمية الذكية للمستندات"""

    def __init__(self, ollama_base_url: str = "http://localhost:11434", model: str = "qwen2:7b"):
        """
        تهيئة محرك التسمية
        
        Args:
            ollama_base_url: عنوان خادم Ollama
            model: اسم نموذج LLM المستخدم
        """
        self.ollama_base_url = ollama_base_url
        self.model = model
        self.timeout = 300
        self.arabic_name_patterns = {
            'عقد': r'عقد\s+([\u0600-\u06FF\s]+)',
            'فاتورة': r'فاتورة\s+([\u0600-\u06FF\s]+)',
            'شهادة': r'شهادة\s+([\u0600-\u06FF\s]+)',
            'خطاب': r'خطاب\s+([\u0600-\u06FF\s]+)',
            'تقرير': r'تقرير\s+([\u0600-\u06FF\s]+)',
            'تصريح': r'تصريح\s+([\u0600-\u06FF\s]+)',
            'إيصال': r'إيصال\s+([\u0600-\u06FF\s]+)',
        }

    def detect_language(self, text: str) -> str:
        """
        اكتشاف لغة النص
        
        Args:
            text: النص المراد اكتشاف لغته
            
        Returns:
            كود اللغة (ar, en, etc.)
        """
        try:
            if not text or len(text.strip()) == 0:
                return "ar"
            language = detect(text[:500])  # استخدم أول 500 حرف
            return language
        except LangDetectException:
            return "ar"  # الافتراضي العربية

    def extract_key_entities(self, text: str) -> Dict[str, List[str]]:
        """
        استخراج الكيانات المهمة من النص (أسماء أشخاص، تواريخ، أرقام، جهات، وغيرها)
        
        Args:
            text: النص المراد استخراج الكيانات منه
            
        Returns:
            قاموس بالكيانات المكتشفة
        """
        entities = {
            'أسماء_أشخاص': [],
            'جهات_ومؤسسات': [],
            'تواريخ': [],
            'أرقام_مالية': [],
            'أرقام_عقود': [],
            'أماكن_وعناوين': [],
            'نسب_مئوية': [],
        }

        # استخراج التواريخ
        date_patterns = [
            r'\d{1,2}[/-]\d{1,2}[/-]\d{4}',  # DD/MM/YYYY أو DD-MM-YYYY
            r'\d{4}[/-]\d{1,2}[/-]\d{1,2}',  # YYYY/MM/DD
            r'(يناير|فبراير|مارس|أبريل|مايو|يونيو|يوليو|أغسطس|سبتمبر|أكتوبر|نوفمبر|ديسمبر)\s+\d{1,2},?\s+\d{4}',
            r'\d{1,2}\s+(يناير|فبراير|مارس|أبريل|مايو|يونيو|يوليو|أغسطس|سبتمبر|أكتوبر|نوفمبر|ديسمبر)\s+\d{4}',
        ]
        for pattern in date_patterns:
            dates = re.findall(pattern, text)
            entities['تواريخ'].extend(dates)

        # استخراج الأرقام المالية (مع العملات)
        money_pattern = r'(\d+(?:[.,]\d{3})*(?:[.,]\d{2})?)\s*(ريال|دولار|يورو|درهم|دينار|جنيه|ليرة|شيقل)'
        money_matches = re.findall(money_pattern, text)
        entities['أرقام_مالية'].extend([f"{amount} {currency}" for amount, currency in money_matches])

        # استخراج أرقام العقود والمراجع
        contract_pattern = r'(رقم|عقد|عقود|شهادة|فاتورة|إيصال)\s+[#:]?\s*([\u0600-\u06FF0-9]+)'
        contract_matches = re.findall(contract_pattern, text)
        entities['أرقام_عقود'].extend([match[1] for match in contract_matches])

        # استخراج النسب المئوية
        percentage_pattern = r'(\d+(?:\.\d{1,2})?)\s*%'
        percentages = re.findall(percentage_pattern, text)
        entities['نسب_مئوية'].extend(percentages)

        # استخراج أسماء الأشخاص والجهات (استخدام اختصارات شائعة)
        name_indicators = r'(السيد|السيدة|الشركة|المؤسسة|الجهة|الموظف|البنك|الفرع)\s+([\u0600-\u06FF\s]+?)(?=[,\.]|\n)'
        name_matches = re.findall(name_indicators, text)
        for match in name_matches:
            name = match[1].strip()
            if len(name) > 2 and len(name) < 100:
                if 'السيدة' in match[0] or 'الموظفة' in match[0]:
                    entities['أسماء_أشخاص'].append(name)
                else:
                    entities['أسماء_أشخاص'].append(name)

        # تنظيف والقضاء على التكرارات
        for key in entities:
            entities[key] = list(set([e.strip() for e in entities[key] if e.strip()]))

        return entities

    def _build_smart_naming_prompt(self, text: str, entities: Dict) -> str:
        """
        بناء برمبت متقدم لاستخراج اسم ذكي بشري
        
        Args:
            text: محتوى المستند
            entities: الكيانات المكتشفة
            
        Returns:
            البرمبت الكامل
        """
        # اختصر النص إذا كان طويلاً جداً
        if len(text) > 3000:
            text = text[:3000]

        prompt = f"""
أنت متخصص في تسمية المستندات العربية بأسماء ذكية وبشرية. مهمتك استخراج اسم يشبه تماماً كيفية تسمية الإنسان العربي للمستند.

**قواعد التسمية الذكية:**
1. الاسم يجب أن يكون واقعياً وكما يسميه الإنسان العربي في الحياة الحقيقية
2. الترتيب: [نوع المستند] - [الشخص/الجهة المسؤولة] - [التفاصيل الإضافية] - [التاريخ]
3. التفاصيل الإضافية قد تكون: رقم شقة، رقم عقد، نوع الخدمة، مبلغ مالي
4. استخدم التواريخ بصيغة واضحة: "يناير 2026" أو "1 يناير 2026"
5. أزل الأرقام العشوائية والرموز الغريبة
6. استخدم فواصل " - " بين الأجزاء
7. الطول: 40-80 حرف عربي

**أمثلة على تسمية صحيحة:**
- عقد إيجار - محمد أحمد العلي - شقة 5 - يناير 2026
- فاتورة كهرباء - شقة 3 - مارس 2026
- شهادة تخرج - سارة محمد - جامعة بغداد - 2025
- فاتورة شراء - متجر الأسواق - 15 فبراير 2026
- تقرير طبي - د. علي المحمود - فحص دوري - مايو 2026

**الكيانات المكتشفة:**
- أسماء: {', '.join(entities.get('أسماء_أشخاص', [])[:3])}
- جهات: {', '.join(entities.get('جهات_ومؤسسات', [])[:2])}
- تواريخ: {', '.join(entities.get('تواريخ', [])[:2])}
- أرقام: {', '.join(entities.get('أرقام_عقود', [])[:2])}
- مبالغ: {', '.join(entities.get('أرقام_مالية', [])[:2])}

**محتوى المستند:**
---
{text}
---

**المطلوب:**
أجب بصيغة JSON فقط بدون أي نص إضافي:
{{
  "document_type": "نوع المستند بالعربية (عقد، فاتورة، شهادة، تقرير، إلخ)",
  "smart_name": "الاسم الذكي الكامل كما يسميه الإنسان العربي",
  "responsible_person": "اسم الشخص أو الجهة المسؤولة",
  "key_details": "التفاصيل المهمة من المستند",
  "date_extracted": "التاريخ بصيغة YYYY-MM-DD أو null",
  "category": "التصنيف (عقود، فواتير، شهادات، خطابات، تقارير، أخرى)",
  "confidence": 0.95,
  "reasoning": "سبب اختيار هذا الاسم"
}}
"""
        return prompt

    def call_ollama_api(self, prompt: str) -> Optional[str]:
        """
        استدعاء API خادم Ollama للحصول على استجابة من النموذج
        
        Args:
            prompt: البرمبت المراد إرساله
            
        Returns:
            الاستجابة من النموذج أو None إذا فشل
        """
        try:
            url = f"{self.ollama_base_url}/api/generate"
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "temperature": 0.3,  # درجة حرارة منخفضة للدقة
                "top_p": 0.9,
                "top_k": 40,
            }

            response = requests.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()

            result = response.json()
            return result.get('response', '')
        except requests.exceptions.ConnectionError:
            logger.error("خطأ: لا يمكن الاتصال بخادم Ollama. تأكد من تشغيل Ollama: ollama serve")
            return None
        except requests.exceptions.Timeout:
            logger.error("خطأ: انتهت مهلة انتظار الاتصال بخادم Ollama")
            return None
        except Exception as e:
            logger.error(f"خطأ في استدعاء Ollama API: {str(e)}")
            return None

    def extract_json_from_response(self, response: str) -> Optional[Dict]:
        """
        استخراج JSON من استجابة النموذج
        
        Args:
            response: استجابة النموذج
            
        Returns:
            قاموس JSON أو None
        """
        try:
            # حاول استخراج JSON من الاستجابة
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                # قم بتنظيف JSON
                json_str = json_str.replace('\n', ' ')
                data = json.loads(json_str)
                return data
            return None
        except json.JSONDecodeError as e:
            logger.error(f"خطأ في تحليل JSON: {str(e)}")
            return None

    def validate_smart_name(self, smart_name: str) -> Tuple[bool, str]:
        """
        التحقق من جودة الاسم الذكي
        
        Args:
            smart_name: الاسم الذكي المراد التحقق منه
            
        Returns:
            (صحيح/خاطئ، رسالة)
        """
        errors = []

        # التحقق من الطول
        if len(smart_name) < 10:
            errors.append("الاسم قصير جداً (أقل من 10 أحرف)")
        if len(smart_name) > 150:
            errors.append("الاسم طويل جداً (أكثر من 150 حرف)")

        # التحقق من وجود أحرف عربية
        if not re.search(r'[\u0600-\u06FF]', smart_name):
            errors.append("الاسم لا يحتوي على أحرف عربية")

        # التحقق من الأحرف غير المسموحة
        forbidden_chars = r'[<>:"/\\|?*]'
        if re.search(forbidden_chars, smart_name):
            errors.append("الاسم يحتوي على أحرف غير مسموحة")

        # التحقق من وجود نوع مستند
        document_types = ['عقد', 'فاتورة', 'شهادة', 'خطاب', 'تقرير', 'صورة', 'تصريح', 'إيصال']
        has_doc_type = any(doc_type in smart_name for doc_type in document_types)
        if not has_doc_type:
            # ليس بالضرورة أن يكون خطأ، لكن تحذير
            pass

        if errors:
            return False, " | ".join(errors)
        return True, "الاسم صالح"

    def generate_smart_name(self, text: str, filename: str = "") -> Dict:
        """
        توليد اسم ذكي بشري للمستند
        
        Args:
            text: محتوى المستند
            filename: اسم الملف الأصلي (اختياري)
            
        Returns:
            قاموس بالتفاصيل الكاملة
        """
        result = {
            'success': False,
            'smart_name': None,
            'document_type': None,
            'responsible_person': None,
            'key_details': None,
            'date_extracted': None,
            'category': None,
            'confidence': 0.0,
            'reasoning': None,
            'original_filename': filename,
            'is_valid': False,
            'validation_message': '',
            'error': None
        }

        try:
            # اكتشاف اللغة
            language = self.detect_language(text)
            if language != 'ar':
                result['error'] = f"لغة المستند ({language}) ليست عربية"
                logger.warning(result['error'])
                # سنحاول على أي حال

            # استخراج الكيانات
            entities = self.extract_key_entities(text)

            # بناء البرمبت
            prompt = self._build_smart_naming_prompt(text, entities)

            # استدعاء Ollama
            logger.info("جاري استدعاء نموذج Ollama للتسمية الذكية...")
            response = self.call_ollama_api(prompt)

            if not response:
                result['error'] = "فشل الاتصال بخادم Ollama"
                logger.error(result['error'])
                return result

            # استخراج JSON
            ai_result = self.extract_json_from_response(response)
            if not ai_result:
                result['error'] = "فشل استخراج النتائج من استجابة الذكاء الاصطناعي"
                logger.error(result['error'])
                return result

            # تعبئة النتائج
            result['document_type'] = ai_result.get('document_type', 'غير محدد')
            result['smart_name'] = ai_result.get('smart_name', 'بدون تسمية')
            result['responsible_person'] = ai_result.get('responsible_person', None)
            result['key_details'] = ai_result.get('key_details', None)
            result['date_extracted'] = ai_result.get('date_extracted', None)
            result['category'] = ai_result.get('category', 'أخرى')
            result['confidence'] = ai_result.get('confidence', 0.5)
            result['reasoning'] = ai_result.get('reasoning', '')

            # التحقق من صحة الاسم
            is_valid, validation_msg = self.validate_smart_name(result['smart_name'])
            result['is_valid'] = is_valid
            result['validation_message'] = validation_msg

            if is_valid:
                result['success'] = True
                logger.info(f"تم توليد اسم ذكي بنجاح: {result['smart_name']}")
            else:
                logger.warning(f"الاسم الذكي لم يمر التحقق: {validation_msg}")

            return result

        except Exception as e:
            result['error'] = f"خطأ غير متوقع: {str(e)}"
            logger.error(result['error'])
            return result

    def improve_name_from_user_feedback(self, original_name: str, user_feedback: str) -> str:
        """
        تحسين الاسم بناءً على تعديل المستخدم
        
        Args:
            original_name: الاسم الأصلي
            user_feedback: تعديل المستخدم
            
        Returns:
            الاسم المحسّن
        """
        # يمكن استخدام هذا لاحقاً للتعلم المستمر
        logger.info(f"تم حفظ تعديل المستخدم: {original_name} → {user_feedback}")
        return user_feedback
