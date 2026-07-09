# -*- coding: utf-8 -*-
"""
مدير قاعدة البيانات
"""

import sqlite3
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    مدير قاعدة البيانات SQLite
    """

    def __init__(self, db_path: str):
        """
        تهيئة مدير قاعدة البيانات
        
        Args:
            db_path: مسار ملف قاعدة البيانات
        """
        self.db_path = db_path
        self.connection = None
        self._connect()

    def _connect(self):
        """
        الاتصال بقاعدة البيانات
        """
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            logger.info(f"تم الاتصال بقاعدة البيانات: {self.db_path}")
        except Exception as e:
            logger.error(f"خطأ في الاتصال بقاعدة البيانات: {str(e)}")
            raise

    def initialize_database(self):
        """
        إنشاء جداول قاعدة البيانات
        """
        try:
            cursor = self.connection.cursor()
            
            # جدول المستندات
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    original_filename TEXT NOT NULL,
                    smart_name TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    archive_path TEXT NOT NULL,
                    file_type TEXT NOT NULL,
                    file_size INTEGER,
                    file_hash TEXT UNIQUE,
                    document_type TEXT,
                    category TEXT,
                    responsible_person TEXT,
                    summary TEXT,
                    full_text TEXT,
                    language TEXT,
                    confidence REAL,
                    date_found TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    is_approved BOOLEAN DEFAULT 0,
                    approved_by TEXT,
                    approved_at DATETIME
                )
            """)
            
            # جدول الكيانات
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS entities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    document_id INTEGER,
                    entity_type TEXT,
                    entity_value TEXT,
                    FOREIGN KEY (document_id) REFERENCES documents(id)
                )
            """)
            
            # جدول التصنيفات
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    parent_id INTEGER,
                    icon TEXT,
                    color TEXT,
                    FOREIGN KEY (parent_id) REFERENCES categories(id)
                )
            """)
            
            # جدول سجل النشاط
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS activity_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    document_id INTEGER,
                    action TEXT,
                    details TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (document_id) REFERENCES documents(id)
                )
            """)
            
            # جدول الوسوم
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL
                )
            """)
            
            # جدول العلاقة بين المستندات والوسوم
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS document_tags (
                    document_id INTEGER,
                    tag_id INTEGER,
                    PRIMARY KEY (document_id, tag_id),
                    FOREIGN KEY (document_id) REFERENCES documents(id),
                    FOREIGN KEY (tag_id) REFERENCES tags(id)
                )
            """)
            
            # إنشاء الفهارس لتحسين الأداء
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_doc_hash ON documents(file_hash)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_doc_category ON documents(category)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_doc_date ON documents(created_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_entity_docid ON entities(document_id)")
            
            self.connection.commit()
            logger.info("تم تهيئة جداول قاعدة البيانات بنجاح")
            
        except Exception as e:
            logger.error(f"خطأ في تهيئة قاعدة البيانات: {str(e)}")
            raise

    def insert_document(self, document_data: Dict) -> Optional[int]:
        """
        إدراج مستند جديد
        
        Args:
            document_data: قاموس بيانات المستند
            
        Returns:
            معرف المستند أو None
        """
        try:
            cursor = self.connection.cursor()
            
            cursor.execute("""
                INSERT INTO documents (
                    original_filename, smart_name, file_path, archive_path,
                    file_type, file_size, file_hash, document_type, category,
                    responsible_person, summary, full_text, language, confidence,
                    date_found, is_approved
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                document_data.get('original_filename'),
                document_data.get('smart_name'),
                document_data.get('file_path'),
                document_data.get('archive_path'),
                document_data.get('file_type'),
                document_data.get('file_size'),
                document_data.get('file_hash'),
                document_data.get('document_type'),
                document_data.get('category'),
                document_data.get('responsible_person'),
                document_data.get('summary'),
                document_data.get('full_text'),
                document_data.get('language'),
                document_data.get('confidence'),
                document_data.get('date_found'),
                document_data.get('is_approved', 0)
            ))
            
            self.connection.commit()
            doc_id = cursor.lastrowid
            logger.info(f"تم إدراج مستند جديد (ID: {doc_id})")
            return doc_id
            
        except sqlite3.IntegrityError as e:
            logger.warning(f"المستند موجود بالفعل (Hash مكرر): {str(e)}")
            return None
        except Exception as e:
            logger.error(f"خطأ في إدراج المستند: {str(e)}")
            return None

    def get_document(self, doc_id: int) -> Optional[Dict]:
        """
        الحصول على بيانات مستند
        
        Args:
            doc_id: معرف المستند
            
        Returns:
            قاموس ببيانات المستند أو None
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM documents WHERE id = ?", (doc_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception as e:
            logger.error(f"خطأ في استرجاع المستند: {str(e)}")
            return None

    def get_all_documents(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """
        الحصول على جميع المستندات
        
        Args:
            limit: عدد النتائج
            offset: الإزاحة
            
        Returns:
            قائمة بالمستندات
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT * FROM documents
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """, (limit, offset))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"خطأ في استرجاع المستندات: {str(e)}")
            return []

    def search_documents(self, query: str, search_fields: List[str] = None) -> List[Dict]:
        """
        البحث عن المستندات
        
        Args:
            query: نص البحث
            search_fields: الحقول المراد البحث فيها
            
        Returns:
            قائمة بالمستندات المطابقة
        """
        try:
            if search_fields is None:
                search_fields = ['smart_name', 'responsible_person', 'full_text']
            
            cursor = self.connection.cursor()
            
            # بناء استعلام البحث
            where_clauses = [f"{field} LIKE ?" for field in search_fields]
            where_sql = " OR ".join(where_clauses)
            query_param = f"%{query}%"
            params = [query_param] * len(search_fields)
            
            cursor.execute(f"""
                SELECT * FROM documents
                WHERE {where_sql}
                ORDER BY created_at DESC
            """, params)
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
            
        except Exception as e:
            logger.error(f"خطأ في البحث: {str(e)}")
            return []

    def get_documents_by_category(self, category: str) -> List[Dict]:
        """
        الحصول على المستندات حسب التصنيف
        
        Args:
            category: التصنيف
            
        Returns:
            قائمة بالمستندات
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("""
                SELECT * FROM documents
                WHERE category = ?
                ORDER BY created_at DESC
            """, (category,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except Exception as e:
            logger.error(f"خطأ في استرجاع المستندات حسب التصنيف: {str(e)}")
            return []

    def update_document(self, doc_id: int, updates: Dict) -> bool:
        """
        تحديث بيانات مستند
        
        Args:
            doc_id: معرف المستند
            updates: قاموس بالتحديثات
            
        Returns:
            نجح أم لا
        """
        try:
            cursor = self.connection.cursor()
            
            # بناء استعلام UPDATE ديناميكي
            set_clauses = [f"{key} = ?" for key in updates.keys()]
            set_sql = ", ".join(set_clauses)
            values = list(updates.values()) + [doc_id]
            
            cursor.execute(f"""
                UPDATE documents
                SET {set_sql}, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, values)
            
            self.connection.commit()
            logger.info(f"تم تحديث المستند (ID: {doc_id})")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في تحديث المستند: {str(e)}")
            return False

    def delete_document(self, doc_id: int) -> bool:
        """
        حذف مستند
        
        Args:
            doc_id: معرف المستند
            
        Returns:
            نجح أم لا
        """
        try:
            cursor = self.connection.cursor()
            
            # حذف الكيانات المرتبطة
            cursor.execute("DELETE FROM entities WHERE document_id = ?", (doc_id,))
            
            # حذف الوسوم المرتبطة
            cursor.execute("DELETE FROM document_tags WHERE document_id = ?", (doc_id,))
            
            # حذف سجل النشاط
            cursor.execute("DELETE FROM activity_log WHERE document_id = ?", (doc_id,))
            
            # حذف المستند
            cursor.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
            
            self.connection.commit()
            logger.info(f"تم حذف المستند (ID: {doc_id})")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في حذف المستند: {str(e)}")
            return False

    def get_statistics(self) -> Dict:
        """
        الحصول على إحصائيات قاعدة البيانات
        
        Returns:
            قاموس بالإحصائيات
        """
        try:
            cursor = self.connection.cursor()
            
            stats = {}
            
            # إجمالي المستندات
            cursor.execute("SELECT COUNT(*) FROM documents")
            stats['total_documents'] = cursor.fetchone()[0]
            
            # المستندات حسب التصنيف
            cursor.execute("""
                SELECT category, COUNT(*) as count
                FROM documents
                GROUP BY category
            """)
            stats['documents_by_category'] = dict(cursor.fetchall())
            
            # إجمالي حجم الملفات
            cursor.execute("SELECT SUM(file_size) FROM documents")
            total_size = cursor.fetchone()[0] or 0
            stats['total_size'] = total_size
            
            # المستندات المعتمدة
            cursor.execute("SELECT COUNT(*) FROM documents WHERE is_approved = 1")
            stats['approved_documents'] = cursor.fetchone()[0]
            
            return stats
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على الإحصائيات: {str(e)}")
            return {}

    def close(self):
        """
        إغلاق الاتصال بقاعدة البيانات
        """
        if self.connection:
            self.connection.close()
            logger.info("تم إغلاق الاتصال بقاعدة البيانات")
