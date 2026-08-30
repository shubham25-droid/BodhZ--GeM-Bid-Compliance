import os
import glob
from typing import List, Dict, Any

class BodhZKnowledgeRetriever:
    """
    RAG Retrieval Engine for BodhZ Knowledge Base.
    Loads modular domain knowledge files and retrieves relevant text chunks
    for context augmentation during OpenAI LLM execution.
    """

    def __init__(self, knowledge_dir: str = None):
        if knowledge_dir is None:
            knowledge_dir = os.path.join(os.path.dirname(__file__), "..", "knowledge")
        self.knowledge_dir = os.path.abspath(knowledge_dir)
        self.documents = []
        self._load_knowledge_files()

    def _load_knowledge_files(self):
        self.documents = []
        if not os.path.exists(self.knowledge_dir):
            return

        pattern = os.path.join(self.knowledge_dir, "**", "*.txt")
        for filepath in glob.glob(pattern, recursive=True):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:
                        filename = os.path.basename(filepath)
                        self.documents.append({
                            "source": filename,
                            "content": content
                        })
            except Exception as e:
                pass

    def retrieve_relevant_knowledge(self, query: str, top_k: int = 3) -> str:
        if not self.documents:
            return ""

        q_terms = set(query.lower().split())
        scored_docs = []

        for doc in self.documents:
            content_lower = doc["content"].lower()
            score = sum(1 for term in q_terms if term in content_lower)
            if score > 0:
                scored_docs.append((score, doc["content"]))

        scored_docs.sort(key=lambda x: x[0], reverse=True)
        top_chunks = [doc[1] for doc in scored_docs[:top_k]]
        return "\n\n".join(top_chunks)
