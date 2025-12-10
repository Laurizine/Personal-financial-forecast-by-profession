import sqlite3
import logging
import json
from datetime import datetime

# Cấu hình logging
logger = logging.getLogger(__name__)

DB_PATH = "credit_scoring.db"

class DatabaseManager:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _get_conn(self):
        """Tạo kết nối thread-safe tới SQLite"""
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def _init_db(self):
        """Khởi tạo schema database"""
        try:
            conn = self._get_conn()
            cursor = conn.cursor()

            # 1. Bảng predictions
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    job TEXT,
                    income REAL,
                    expense REAL,
                    debt REAL,
                    income_ratio REAL,
                    debt_ratio REAL,
                    rule_class TEXT,
                    bayes_class TEXT,
                    bayes_score REAL,
                    final_class TEXT,
                    llm_cache_key TEXT,
                    processing_time REAL
                )
            """)

            # 2. Bảng llm_cache
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS llm_cache (
                    input_hash TEXT PRIMARY KEY,
                    explanation TEXT,
                    model_name TEXT,
                    created_at TEXT,
                    expires_at TEXT
                )
            """)

            # 3. Bảng fired_rules
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS fired_rules (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prediction_id INTEGER,
                    rule_name TEXT,
                    FOREIGN KEY(prediction_id) REFERENCES predictions(id)
                )
            """)

            # Tạo Index
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_pred_created ON predictions(created_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_cache_hash ON llm_cache(input_hash)")

            conn.commit()
            logger.info("Database initialized successfully.")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def log_prediction(self, facts, result, duration=0.0):
        """
        Ghi log dự đoán vào bảng predictions.
        Trả về id của bản ghi vừa tạo.
        """
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            
            bayes = result.get("bayesian", {})
            rule_conclusions = result.get("rule_conclusions", {})
            
            # Map dữ liệu từ facts và result
            created_at = datetime.now().isoformat()
            
            # Tính toán cache key nếu chưa có (thường controller sẽ pass vào, nhưng ở đây ta giả định key là input hash)
            # Trong controller hiện tại, cache key được tạo ra nhưng không lưu trong result.
            # Ta sẽ lấy từ facts hoặc để NULL nếu không cần thiết, hoặc sửa controller để truyền vào.
            # Ở đây tạm thời để NULL hoặc lấy từ facts nếu có.
            llm_cache_key = facts.get("cache_key") 

            cursor.execute("""
                INSERT INTO predictions (
                    created_at, job, income, expense, debt, 
                    income_ratio, debt_ratio, 
                    rule_class, bayes_class, bayes_score, final_class, 
                    llm_cache_key, processing_time
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                created_at,
                facts.get("job"),
                facts.get("income_monthly"),
                facts.get("expense_monthly"),
                facts.get("debt_amount"),
                facts.get("income_expense_ratio"),
                facts.get("debt_ratio"),
                rule_conclusions.get("rule_credit_class"),
                bayes.get("bayes_class"),
                bayes.get("bayes_score"),
                result.get("final_class"),
                llm_cache_key,
                duration
            ))
            
            prediction_id = cursor.lastrowid
            conn.commit()
            return prediction_id

        except Exception as e:
            logger.error(f"Failed to log prediction: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def log_fired_rules(self, prediction_id, fired_rules):
        """
        Lưu danh sách luật đã kích hoạt vào bảng fired_rules
        """
        if not prediction_id or not fired_rules:
            return

        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            
            data = [(prediction_id, rule_name) for rule_name in fired_rules]
            
            cursor.executemany("""
                INSERT INTO fired_rules (prediction_id, rule_name)
                VALUES (?, ?)
            """, data)
            
            conn.commit()
        except Exception as e:
            logger.error(f"Failed to log fired rules: {e}")
        finally:
            if conn:
                conn.close()

    def get_cached_explanation(self, input_hash):
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            cursor.execute("SELECT explanation FROM llm_cache WHERE input_hash = ?", (input_hash,))
            row = cursor.fetchone()
            if row:
                logger.debug(f"Cache HIT for hash {input_hash}")
                return row[0]
            return None
        except Exception as e:
            logger.error(f"DB Cache read error: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def save_cached_explanation(self, input_hash, explanation, model_name="gemini"):
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO llm_cache (input_hash, explanation, model_name, created_at, expires_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                input_hash, 
                explanation, 
                model_name,
                datetime.now().isoformat(),
                None # Chưa dùng logic expires
            ))
            conn.commit()
            logger.debug(f"Cache SAVED for hash {input_hash}")
        except Exception as e:
            logger.error(f"DB Cache write error: {e}")
        finally:
            if conn:
                conn.close()
