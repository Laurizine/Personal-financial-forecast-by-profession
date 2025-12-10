import sqlite3
import json
import time
import os
import logging
from datetime import datetime

DB_PATH = "credit_scoring.db"
logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _get_conn(self):
        return sqlite3.connect(self.db_path, check_same_thread=False)

    def _init_db(self):
        """Khởi tạo bảng nếu chưa tồn tại"""
        conn = self._get_conn()
        cursor = conn.cursor()
        
        # Bảng 1: prediction_logs
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prediction_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT,
                job TEXT,
                income REAL,
                debt REAL,
                input_json TEXT,
                rule_class TEXT,
                bayes_class TEXT,
                bayes_score REAL,
                final_class TEXT,
                processing_time REAL
            )
        """)
        
        # Bảng 2: llm_cache
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS llm_cache (
                input_hash TEXT PRIMARY KEY,
                explanation TEXT,
                model_name TEXT,
                created_at TEXT
            )
        """)
        
        conn.commit()
        conn.close()

    # ==========================
    # LOGGING FUNCTIONS
    # ==========================
    def log_prediction(self, facts, result, duration=0.0):
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            
            bayes = result.get("bayesian", {})
            rule_conclusions = result.get("rule_conclusions", {})
            
            cursor.execute("""
                INSERT INTO prediction_logs (
                    created_at, job, income, debt, input_json, 
                    rule_class, bayes_class, bayes_score, final_class, processing_time
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                facts.get("job"),
                facts.get("income_monthly"),
                facts.get("debt_amount"),
                json.dumps(facts, ensure_ascii=False),
                rule_conclusions.get("rule_credit_class"),
                bayes.get("bayes_class"),
                bayes.get("bayes_score"),
                result.get("final_class"),
                duration
            ))
            
            conn.commit()
            conn.close()
            logger.debug("Saved prediction log to database.")
        except Exception as e:
            logger.error(f"Failed to log prediction: {e}")

    # ==========================
    # CACHE FUNCTIONS
    # ==========================
    def get_cached_explanation(self, input_hash):
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            cursor.execute("SELECT explanation FROM llm_cache WHERE input_hash = ?", (input_hash,))
            row = cursor.fetchone()
            conn.close()
            if row:
                logger.debug(f"Cache HIT for hash {input_hash}")
                return row[0]
            return None
        except Exception as e:
            logger.error(f"DB Cache read error: {e}")
            return None

    def save_cached_explanation(self, input_hash, explanation, model_name="gemini"):
        try:
            conn = self._get_conn()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO llm_cache (input_hash, explanation, model_name, created_at)
                VALUES (?, ?, ?, ?)
            """, (
                input_hash, 
                explanation, 
                model_name,
                datetime.now().isoformat()
            ))
            conn.commit()
            conn.close()
            logger.debug(f"Cache SAVED for hash {input_hash}")
        except Exception as e:
            logger.error(f"DB Cache write error: {e}")
