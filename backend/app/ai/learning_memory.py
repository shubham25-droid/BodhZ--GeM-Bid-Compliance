import os
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# --------------------------------------------------
# DYNAMIC LEARNING MEMORY SYSTEM (SIH26100)
# --------------------------------------------------
class BodhZLearningMemory:
    """
    Persistent Learning Memory for BodhZ AI Chatbot.
    Stores and retrieves past user Q&A interactions, learned facts, and contextual preferences
    so the AI continuously learns from past conversations for future queries.
    """

    def __init__(self, memory_file_path: str = None):
        if memory_file_path is None:
            base_dir = os.path.dirname(__file__)
            memory_dir = os.path.abspath(os.path.join(base_dir, "..", "knowledge", "learning_memory"))
            os.makedirs(memory_dir, exist_ok=True)
            memory_file_path = os.path.join(memory_dir, "learned_qa.json")

        self.memory_file = memory_file_path
        self.memory_store: List[Dict[str, Any]] = self._load_memory()

    def _load_memory(self) -> List[Dict[str, Any]]:
        if os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        return data
            except Exception as e:
                logger.error(f"Failed to load learning memory: {e}")
        return []

    def save_learned_interaction(self, question: str, answer: str, source: str = "INTERACTION"):
        """Saves a new user Q&A pair into persistent memory."""
        if not question or not answer:
            return

        # Avoid duplicate consecutive entries
        clean_q = question.strip()
        clean_a = answer.strip()
        
        for item in self.memory_store[-10:]:
            if item.get("question", "").lower() == clean_q.lower():
                return

        record = {
            "timestamp": datetime.now().isoformat(),
            "question": clean_q,
            "answer": clean_a,
            "source": source
        }
        self.memory_store.append(record)

        try:
            with open(self.memory_file, "w", encoding="utf-8") as f:
                json.dump(self.memory_store, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save learning memory: {e}")

    def retrieve_relevant_memory(self, query: str, limit: int = 3) -> str:
        """Retrieves past learned Q&A interactions relevant to the current query."""
        if not self.memory_store:
            return ""

        q_words = set(query.lower().split())
        matched = []

        for item in reversed(self.memory_store):
            stored_q = item.get("question", "").lower()
            stored_a = item.get("answer", "")
            
            # Count word overlaps
            overlap = sum(1 for w in q_words if w in stored_q or w in stored_a.lower())
            if overlap > 0:
                matched.append(f"Past Question: {item['question']}\nLearned Answer: {item['answer']}")
                if len(matched) >= limit:
                    break

        if matched:
            return "\n\n".join(matched)
        return ""
