# 📋 دليل التثبيت والاختبار والصيانة الشامل

## 🚀 **البدء السريع (5 دقائق)**

### الخطوة 1: التثبيت
```bash
git clone https://github.com/Almoon866/Smart-archive.git
cd Smart-archive
python -m venv venv
venv\Scripts\activate  # على Windows
# أو على Linux/macOS:
# source venv/bin/activate
pip install -r requirements.txt
```

### الخطوة 2: تثبيت Ollama
```bash
# اذهب إلى https://ollama.ai/download
# ثم شغّل في Terminal جديد:
ollama serve
```

### الخطوة 3: التشغيل
```bash
python main.py
```

---

## ✅ **اختبار المشروع**

### **اختبار شامل لجميع المكونات**
```bash
# تفعيل البيئة أولاً
venv\Scripts\activate

# تشغيل الاختبار الشامل
python test_app.py
```

### **ما يتم اختباره:**
- ✅ استيراد المكتبات الأساسية
- ✅ تحميل المحركات (7 محركات)
- ✅ قاعدة البيانات وإنشاء الجداول
- ✅ واجهة المستخدم (الشاشات 6)
- ✅ الأدوات المساعدة (Logger, File Utils, Text Utils)
- ✅ وجود المجلدات المطلوبة

### **النتائج المتوقعة:**
```
✅ الاستيرادات
✅ المحركات
✅ قاعدة البيانات
✅ واجهة المستخدم
✅ الأدوات
✅ المجلدات

📊 النتيجة الإجمالية: 6/6 نجح
🎉 كل الاختبارات نجحت! يمكنك الآن تشغيل: python main.py
```

---

## 🔧 **الصيانة والمشاكل الشائعة**

### **المشكلة 1: Ollama غير متاح**
```
❌ ollama موت متاح
```
**الحل:**
```bash
# 1. تحقق من تثبيت Ollama
ollama --version

# 2. إذا لم يكن مثبتاً، حمّله من:
# https://ollama.ai/download

# 3. إذا كان مثبتاً، شغّل Server في Terminal جديد:
ollama serve

# 4. اختبر الاتصال:
curl http://localhost:11434/api/tags
```

### **المشكلة 2: مكتبات مفقودة**
```
❌ No module named 'PyQt6'
```
**الحل:**
```bash
pip install -r requirements.txt --upgrade
pip install PyQt6==6.5.0
```

### **المشكلة 3: قاعدة البيانات معطوبة**
```
❌ database is locked
```
**الحل:**
```bash
# حذف قاعدة البيانات القديمة (سيتم إنشاء جديدة):
rm database/documents.db

# ثم شغّل التطبيق مرة أخرى:
python main.py
```

### **المشكلة 4: مشاكل في الأداء**
```
⚠️ التطبيق بطيء أو يتعطل
```
**الحل:**
```bash
# 1. تحقق من استخدام الذاكرة:
# في Task Manager (Windows) أو htop (Linux)

# 2. قلل حجم نماذج OCR:
# في config.py ، غيّر:
OCR_USE_GPU = False
OCR_SHOW_LOG = False

# 3. استخدم نموذج أصغر من Ollama:
ollama pull qwen2:1.5b  # بدلاً من 7b
```

---

## 📊 **عرض المشروع**

### **الشاشات الرئيسية:**

#### 1. **لوحة التحكم (Dashboard)**
- إحصائيات عامة
- عدد المستندات
- آخر الملفات المستوردة
- الإحصائيات الشهرية

#### 2. **شاشة الاستيراد (Import)**
- سحب وإفلات الملفات
- معاينة المستندات
- تصحيح الأسماء الذكية
- تعيين التصنيفات

#### 3. **مدير المستندات (Manager)**
- عرض جميع المستندات
- تعديل البيانات الوصفية
- حذف أو إعادة تسمية
- عرض المسار

#### 4. **البحث المتقدم (Search)**
- بحث بالاسم
- بحث بالمحتوى
- فلاتر متعددة
- نتائج فورية

#### 5. **التقارير والإحصائيات (Reports)**
- رسوم بيانية
- إحصائيات شهرية/سنوية
- تحليل الاستخدام
- تصدير التقارير

#### 6. **الإعدادات (Settings)**
- تغيير مسار الأرشفة
- إعدادات AI و OCR
- إدارة التصنيفات
- النسخ الاحتياطي والاستعادة

---

## 🔍 **اختبار الميزات**

### **1. اختبار الاستيراد**
```python
# في اختبار يدوي:
from engines.import_engine import ImportEngine

# اختبر استيراد ملف PDF
engine = ImportEngine()
result = engine.import_file("path/to/file.pdf")
print(result)  # يجب أن يعيد معلومات الملف
```

### **2. اختبار الاستخراج**
```python
from engines.extraction_engine import ExtractionEngine

engine = ExtractionEngine()
text = engine.extract_text("path/to/file.pdf")
print(text)  # يجب أن يعيد النص المستخرج
```

### **3. اختبار OCR**
```python
from engines.ocr_engine import OCREngine

engine = OCREngine()
text = engine.recognize_text("path/to/image.png")
print(text)  # يجب أن يعيد النص المتعرف عليه
```

### **4. اختبار التسمية الذكية**
```python
from engines.naming_engine import NamingEngine

engine = NamingEngine()
name = engine.generate_smart_name("محتوى المستند هنا")
print(name)  # يجب أن يعيد اسم ذكي
```

### **5. اختبار قاعدة البيانات**
```python
from database.db_manager import DatabaseManager
import config

db = DatabaseManager(str(config.DATABASE_PATH))
db.initialize_database()

# إدراج مستند
doc_data = {
    'filename': 'test.pdf',
    'smart_name': 'عقد توظيف',
    'category': 'عقود ووثائق قانونية',
}
db.insert_document(**doc_data)

# استرجاع المستندات
docs = db.get_all_documents()
print(f"عدد المستندات: {len(docs)}")
```

---

## 🐛 **نصائح للصيانة**

### **1. تنظيف السجلات**
```bash
# حذف ملفات السجلات القديمة
rm logs/*.log

# أو احتفظ بالحديثة فقط
find logs/ -mtime +30 -delete  # حذف أقدم من 30 يوم
```

### **2. النسخ الاحتياطي**
```bash
# النسخ الاحتياطي اليدوي
cp database/documents.db database/backups/documents_backup_$(date +%Y%m%d_%H%M%S).db

# أو استخدم الأمر من الواجهة: Settings → Backup
```

### **3. تحديث المكتبات**
```bash
# تحديث جميع المكتبات
pip install -r requirements.txt --upgrade

# أو تحديث محددة
pip install PyQt6==6.6.0 --upgrade
```

### **4. مراقبة الأداء**
```bash
# تتبع استخدام الموارد أثناء التشغيل
# على Windows:
tasklist /fi "IMAGENAME eq python.exe" /v

# على Linux:
ps aux | grep python
```

---

## 📈 **تحسينات مستقبلية**

### **قصيرة المدى:**
- [ ] إضافة المزيد من صيغ الملفات
- [ ] تحسين سرعة OCR
- [ ] دعم النماذج الإنجليزية

### **متوسطة المدى:**
- [ ] واجهة ويب
- [ ] تطبيق موبايل
- [ ] تصفية أذكى للنتائج

### **طويلة المدى:**
- [ ] دعم المزامنة السحابية
- [ ] نموذج AI مخصص
- [ ] نظام أذونات متقدم

---

## 📞 **الدعم والمساعدة**

### **الأخطاء الشائعة:**

| المشكلة | الحل |
|--------|------|
| Ollama غير متاح | شغّل `ollama serve` في Terminal جديد |
| مكتبات مفقودة | `pip install -r requirements.txt` |
| قاعدة البيانات معطوبة | احذف `database/documents.db` |
| OCR بطيء | استخدم `OCR_USE_GPU = True` إذا كان GPU متاحاً |
| الواجهة تتعطل | راجع `logs/app.log` للأخطاء |

### **الملفات المهمة:**
- 📍 `logs/app.log` - سجل الأخطاء والأحداث
- 📍 `database/documents.db` - قاعدة البيانات الرئيسية
- 📍 `config.py` - الإعدادات الرئيسية
- 📍 `requirements.txt` - المكتبات المطلوبة

---

## 🎉 **تم!**

الآن أنت مستعد لـ:
- ✅ تشغيل التطبيق
- ✅ اختبار جميع الميزات
- ✅ صيانة واستكشاف الأخطاء
- ✅ تحسين الأداء

**ابدأ بـ:**
```bash
venv\Scripts\activate
python test_app.py
python main.py
```

---

**تاريخ التحديث:** يوليو 2026  
**الإصدار:** 1.0.0  
**المطور:** Almoon866
