import time
import threading
import structlog

logger = structlog.get_logger(__name__)


class ConversationMemory:
    def __init__(self, ttl_seconds: int = 3600, max_messages: int = 100, max_sessions: int = 1000):
        self.ttl_seconds = ttl_seconds
        self.max_messages = max_messages
        self.max_sessions = max_sessions
        self.sessions: dict = {}
        self._lock = threading.Lock()

    def add_message(self, session_id: str, role: str, content: str):
        with self._lock:
            self._ensure_session(session_id)
            self.sessions[session_id]["messages"].append({
                "role": role,
                "content": content,
                "timestamp": time.time(),
            })
            self.sessions[session_id]["last_active"] = time.time()
            if len(self.sessions[session_id]["messages"]) > self.max_messages:
                self.sessions[session_id]["messages"] = self.sessions[session_id]["messages"][-self.max_messages:]

    def get_messages(self, session_id: str) -> list:
        with self._lock:
            self._ensure_session(session_id)
            return list(self.sessions[session_id]["messages"])

    def get_recent_messages(self, session_id: str, n: int = 10) -> list:
        with self._lock:
            self._ensure_session(session_id)
            return self.sessions[session_id]["messages"][-n:]

    def set_context(self, session_id: str, key: str, value):
        with self._lock:
            self._ensure_session(session_id)
            self.sessions[session_id]["context"][key] = value
            self.sessions[session_id]["last_active"] = time.time()

    def get_context(self, session_id: str, key: str = None):
        with self._lock:
            self._ensure_session(session_id)
            if key:
                return self.sessions[session_id]["context"].get(key)
            return dict(self.sessions[session_id]["context"])

    def clear_session(self, session_id: str):
        with self._lock:
            if session_id in self.sessions:
                del self.sessions[session_id]

    def cleanup_expired(self):
        with self._lock:
            now = time.time()
            expired = [
                sid for sid, data in self.sessions.items()
                if now - data["last_active"] > self.ttl_seconds
            ]
            for sid in expired:
                del self.sessions[sid]
            if expired:
                logger.info("memory_cleanup", expired_count=len(expired))

            if len(self.sessions) > self.max_sessions:
                sorted_sessions = sorted(
                    self.sessions.items(), key=lambda x: x[1]["last_active"]
                )
                to_remove = len(self.sessions) - self.max_sessions
                for sid, _ in sorted_sessions[:to_remove]:
                    del self.sessions[sid]
                logger.info("memory_lru_evict", evicted_count=to_remove)

    def _ensure_session(self, session_id: str):
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "messages": [],
                "context": {},
                "last_active": time.time(),
            }
