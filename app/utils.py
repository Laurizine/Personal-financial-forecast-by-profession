import logging
import time

class RateLimitFilter(logging.Filter):
    """
    Filter log records to suppress duplicates within a time window.
    """
    def __init__(self, window_seconds=5.0, max_records=3):
        super().__init__()
        self.window = float(window_seconds)
        self.max_records = int(max_records)
        self.bucket = {}

    def filter(self, record):
        # Key unique cho mỗi loại log message
        key = (record.name, record.msg)
        now = time.time()
        
        # Lấy danh sách timestamp của key này
        ts = self.bucket.get(key, [])
        
        # Chỉ giữ lại các timestamp trong cửa sổ thời gian
        ts = [t for t in ts if now - t <= self.window]
        
        if len(ts) < self.max_records:
            ts.append(now)
            self.bucket[key] = ts
            return True
        else:
            return False
