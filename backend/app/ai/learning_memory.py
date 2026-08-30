import os
import re
import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


# --------------------------------------------------
# DYNAMIC LEARNING & ADAPTIVE MEMORY SYSTEM (SIH26100)
# --------------------------------------------------
class BodhZLearningMemory:
    """
    Advanced Multi-Tier Adaptive Memory System for BodhZ AI Chatbot.
    Features:
    1. Multi-Turn In-Conversation Memory (Recalls past questions, previous answers, context).
    2. Persistent User Fact Memory (Saves custom notes, turnover, PAN, entity preferences via DB + JSON).
    3. Memory Ingestion & Natural Recall in English & Hinglish ("yaad rakhna", "tune kya yaad rakha hai").
    4. Dynamic Context Grounding (Injects known facts into LLM & Universal QA prompts).
    5. Conversation Summarization on demand.
    """

    def __init__(self, memory_file_path: str = None):
        base_dir = os.path.dirname(__file__)
        memory_dir = os.path.abspath(os.path.join(base_dir, "..", "knowledge", "learning_memory"))
        os.makedirs(memory_dir, exist_ok=True)
        
        self.memory_file = memory_file_path or os.path.join(memory_dir, "learned_qa.json")
        self.user_facts_file = os.path.join(memory_dir, "user_facts.json")
        
        self.memory_store: List[Dict[str, Any]] = self._load_json(self.memory_file, default=[])
        self.user_facts_store: Dict[str, Dict[str, Any]] = self._load_json(self.user_facts_file, default={})

    def _load_json(self, file_path: str, default: Any) -> Any:
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load {file_path}: {e}")
        return default

    def _save_json(self, file_path: str, data: Any):
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save {file_path}: {e}")

    # --------------------------------------------------
    # 1. USER FACT MEMORY (EXPLICIT FACT STORAGE)
    # --------------------------------------------------
    def save_user_fact(
        self,
        user_key: str,
        fact_key: str,
        fact_value: str,
        category: str = "GENERAL",
        source_query: Optional[str] = None,
        db: Optional[Session] = None
    ) -> Dict[str, Any]:
        """Saves or updates a personalized fact in persistent store and database."""
        u_key = (user_key or "default_user").strip().lower()
        f_key = fact_key.strip().lower()
        f_val = fact_value.strip()

        if u_key not in self.user_facts_store:
            self.user_facts_store[u_key] = {}

        now_iso = datetime.now(timezone.utc).isoformat()
        fact_data = {
            "fact_key": f_key,
            "fact_value": f_val,
            "category": category,
            "source_query": source_query or "",
            "updated_at": now_iso
        }
        self.user_facts_store[u_key][f_key] = fact_data
        self._save_json(self.user_facts_file, self.user_facts_store)

        # Database synchronization if DB session is provided
        if db:
            try:
                from app.models.models import UserMemoryFactModel
                existing = db.query(UserMemoryFactModel).filter(
                    UserMemoryFactModel.user_key == u_key,
                    UserMemoryFactModel.fact_key == f_key
                ).first()
                if existing:
                    existing.fact_value = f_val
                    existing.category = category
                    existing.source_query = source_query
                else:
                    new_fact = UserMemoryFactModel(
                        user_key=u_key,
                        fact_key=f_key,
                        fact_value=f_val,
                        category=category,
                        source_query=source_query
                    )
                    db.add(new_fact)
                db.commit()
            except Exception as e:
                logger.warning(f"Could not persist UserMemoryFactModel to DB: {e}")

        logger.info(f"User Fact Stored for [{u_key}]: {f_key} -> {f_val}")
        return fact_data

    def get_user_facts(self, user_key: str, db: Optional[Session] = None) -> Dict[str, str]:
        """Returns all known facts for the given user."""
        u_key = (user_key or "default_user").strip().lower()
        facts = {}

        # 1. From JSON cache
        if u_key in self.user_facts_store:
            for k, v in self.user_facts_store[u_key].items():
                facts[k] = v.get("fact_value", "")

        # 2. From Database if available
        if db:
            try:
                from app.models.models import UserMemoryFactModel
                db_facts = db.query(UserMemoryFactModel).filter(UserMemoryFactModel.user_key == u_key).all()
                for df in db_facts:
                    facts[df.fact_key] = df.fact_value
            except Exception as e:
                logger.warning(f"Could not read UserMemoryFactModel from DB: {e}")

        return facts

    def clear_user_facts(self, user_key: str, db: Optional[Session] = None) -> bool:
        """Clears all facts stored for a user."""
        u_key = (user_key or "default_user").strip().lower()
        if u_key in self.user_facts_store:
            del self.user_facts_store[u_key]
            self._save_json(self.user_facts_file, self.user_facts_store)

        if db:
            try:
                from app.models.models import UserMemoryFactModel
                db.query(UserMemoryFactModel).filter(UserMemoryFactModel.user_key == u_key).delete()
                db.commit()
            except Exception as e:
                logger.warning(f"Could not delete UserMemoryFactModel from DB: {e}")

        return True

    def delete_user_fact(self, user_key: str, fact_key: str, db: Optional[Session] = None) -> bool:
        """Deletes a specific fact key for a user."""
        u_key = (user_key or "default_user").strip().lower()
        f_key = fact_key.strip().lower()

        if u_key in self.user_facts_store and f_key in self.user_facts_store[u_key]:
            del self.user_facts_store[u_key][f_key]
            self._save_json(self.user_facts_file, self.user_facts_store)

        if db:
            try:
                from app.models.models import UserMemoryFactModel
                db.query(UserMemoryFactModel).filter(
                    UserMemoryFactModel.user_key == u_key,
                    UserMemoryFactModel.fact_key == f_key
                ).delete()
                db.commit()
            except Exception as e:
                logger.warning(f"Could not delete UserMemoryFactModel key from DB: {e}")

        return True

    # --------------------------------------------------
    # 2. MEMORY INTENT DETECTOR & PARSER
    # --------------------------------------------------
    def detect_memory_intent(self, query: str) -> Tuple[Optional[str], Optional[Dict[str, Any]]]:
        """
        Detects if the user query is a memory management instruction or memory query.
        Returns (intent_name, metadata).
        """
        raw_q = query.strip()
        q = raw_q.lower()

        # A. Store a Fact ("remember that...", "yaad rakhna...", "note kar lo ki...")
        store_patterns = [
            r"^(?:please\s+)?remember\s+(?:that\s+)?(?:my\s+)?(.+)",
            r"^yaad\s+rakhna\s+(?:ki\s+)?(.+)",
            r"^yaad\s+rakh\s+(?:ki\s+)?(.+)",
            r"^note\s+(?:kar\s+lo|down\s+that|this)\s*[:\s]+(.+)",
            r"^meri\s+memory\s+me\s+save\s+karo\s*[:\s]+(.+)",
            r"^save\s+(?:this\s+)?in\s+memory\s*[:\s]+(.+)",
            r"^keep\s+in\s+mind\s+(?:that\s+)?(.+)"
        ]
        for pat in store_patterns:
            m = re.search(pat, raw_q, re.IGNORECASE)
            if m:
                extracted = m.group(1).strip()
                # Parse key-value (e.g. "my turnover is 15 cr" -> key: turnover, val: 15 cr)
                kv_match = re.search(
                    r"^(?:my\s+|mera\s+|meri\s+)?([a-zA-Z0-9_\s]{2,30}?)\s+(?:is|=|hai|equal\s+to|equals|naam\s+hai|name\s+is)\s+(.+)",
                    extracted,
                    re.IGNORECASE
                )
                if kv_match:
                    f_key = kv_match.group(1).strip().replace(" ", "_").lower()
                    f_val = kv_match.group(2).strip()
                    # Strip trailing copula "hai" in Hindi
                    f_val = re.sub(r"\s+hai$", "", f_val, flags=re.IGNORECASE).strip()
                else:
                    f_key = "custom_note"
                    f_val = extracted
                    f_val = re.sub(r"\s+hai$", "", f_val, flags=re.IGNORECASE).strip()

                return "STORE_FACT", {"fact_key": f_key, "fact_value": f_val, "raw_fact": extracted}

        # B. Recall Previous Question ("maine pehle kya pucha tha", "what did I ask before", "pichla sawal kya tha")
        if any(p in q for p in [
            "maine pehle kya pucha", "maine pehle kya poocha", "pichla sawal", "pichhla sawal",
            "what did i ask", "what was my last question", "what was my previous question",
            "last question", "previous question", "pichla question", "mera last query"
        ]):
            return "RECALL_PREVIOUS_QUESTION", {}

        # C. Recall Previous Answer ("pichla answer kya tha", "what did you say before", "what was your last reply")
        if any(p in q for p in [
            "pichla answer", "pichla reply", "what was your last answer", "what did you say before",
            "what did you answer", "what was your reply", "your previous response"
        ]):
            return "RECALL_PREVIOUS_ANSWER", {}

        # D. View All Stored Memories ("what do you remember about me", "tune mere baare me kya yaad rakha hai", "show my memory")
        if any(p in q for p in [
            "what do you remember about me", "what do you remember", "tune mere baare me kya yaad rakha",
            "kya yaad rakha hai", "show my memory", "list memories", "my saved memories",
            "what facts do you know about me", "show all memory", "show memories", "kya yaad hai"
        ]):
            return "RECALL_ALL_FACTS", {}

        # E. Specific Fact Inquiry ("what is my turnover", "mera turnover kitna hai", "meri company ka naam kya hai")
        fact_inquiry_patterns = [
            r"^(?:what\s+is\s+my|tell\s+me\s+my)\s+([a-zA-Z0-9_\s]{2,30}?)(?:\s*\?)?$",
            r"^(?:mera|meri)\s+([a-zA-Z0-9_\s]{2,30}?)\s+(?:kitna\s+hai|kya\s+hai|batao|kitna\s+tha|kya\s+tha)(?:\s*\?)?$",
            r"^(?:mera|meri)\s+([a-zA-Z0-9_\s]{2,30}?)(?:\s*\?)?$"
        ]
        for pat in fact_inquiry_patterns:
            m = re.search(pat, q)
            if m:
                target_key = m.group(1).strip().replace(" ", "_")
                # Remove common words like 'ka_naam' -> 'name' or 'company_ka_naam' -> 'company_name'
                target_key = target_key.replace("_ka_naam", "").replace("_ki_detail", "")
                return "QUERY_SPECIFIC_FACT", {"fact_key": target_key}

        # F. Conversation Summarization ("summarize our chat", "abhi tak ki baat summarize karo", "what did we discuss so far")
        if any(p in q for p in [
            "summarize our conversation", "summarize our chat", "summarize this conversation",
            "summary of our chat", "abhi tak ki baat", "humne kya discuss kiya", "what did we discuss",
            "recap our conversation", "chat recap", "conversation summary"
        ]):
            return "SUMMARIZE_CONVERSATION", {}

        # G. Clear / Forget Memory ("forget my turnover", "clear memory", "memory delete karo", "reset memory")
        if any(p in q for p in [
            "clear my memory", "clear memory", "reset memory", "memory delete", "memory delete karo",
            "sab bhool jao", "forget everything", "erase memory"
        ]):
            return "CLEAR_ALL_FACTS", {}

        forget_match = re.search(r"(?:forget|bhool\s+jao)\s+(?:my\s+|mera\s+|meri\s+)?([a-zA-Z0-9_\s]{2,30})", q)
        if forget_match:
            f_key = forget_match.group(1).strip().replace(" ", "_")
            return "FORGET_SPECIFIC_FACT", {"fact_key": f_key}

        return None, None

    # --------------------------------------------------
    # 3. EXECUTE MEMORY OPERATIONS & GENERATE DIRECT ANSWERS
    # --------------------------------------------------
    def process_memory_operation(
        self,
        intent: str,
        meta: Dict[str, Any],
        user_key: str,
        user_name: str,
        user_role: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        db: Optional[Session] = None
    ) -> Optional[str]:
        """Executes the memory action and returns a tailored response."""
        u_key = user_key or user_name or "default_user"
        officer = user_name or "Officer"

        if intent == "STORE_FACT":
            f_key = meta["fact_key"]
            f_val = meta["fact_value"]
            self.save_user_fact(u_key, f_key, f_val, category="CUSTOM_FACT", source_query=meta.get("raw_fact"), db=db)
            return (
                f"🧠 **Memory Updated!**\n\n"
                f"I have remembered this fact for your profile:\n"
                f"• **{f_key.replace('_', ' ').title()}**: `{f_val}`\n\n"
                f"I will remember this across our conversations. You can ask me anytime or tell me to update/forget it!"
            )

        elif intent == "RECALL_PREVIOUS_QUESTION":
            if not conversation_history or len(conversation_history) < 1:
                return f"Officer {officer}, this appears to be the start of our session, so there are no earlier questions recorded yet."
            
            # Find the most recent user question before the current one
            user_questions = [h.get("text", "") for h in conversation_history if h.get("sender") == "user"]
            if not user_questions:
                return "You haven't asked any previous questions in this current session yet."
            
            last_q = user_questions[-1]
            earlier_qs = user_questions[:-1]
            
            lines = [f"🧠 **Conversation History Memory:**\n\n• **Your Previous Question Was:**\n> \"{last_q}\""]
            if earlier_qs:
                lines.append(f"\n• **Earlier Questions in This Session ({len(earlier_qs)}):**")
                for idx, q_text in enumerate(reversed(earlier_qs[-4:]), 1):
                    lines.append(f"  {idx}. \"{q_text}\"")
            
            return "\n".join(lines)

        elif intent == "RECALL_PREVIOUS_ANSWER":
            if not conversation_history or len(conversation_history) < 1:
                return "There are no previous assistant replies in this session yet."
            
            bot_answers = [h.get("text", "") for h in conversation_history if h.get("sender") == "assistant" or h.get("sender") == "bot"]
            if not bot_answers:
                return "I haven't provided any previous responses in this session yet."
            
            last_a = bot_answers[-1]
            return f"🧠 **Previous Assistant Response Was:**\n\n{last_a[:600]}..."

        elif intent == "RECALL_ALL_FACTS":
            facts = self.get_user_facts(u_key, db=db)
            if not facts:
                return (
                    f"🧠 **Memory Status for {officer}:**\n\n"
                    f"I currently do not have any custom saved personal facts for your profile yet.\n\n"
                    f"You can tell me anything to remember, for example:\n"
                    f"• *\"Remember that my company is Tata Advanced Training\"*\n"
                    f"• *\"Yaad rakhna mera annual turnover 15 Crores hai\"*\n"
                    f"• *\"Note kar lo ki hum MSME exemption claim kar rahe hain\"*"
                )
            
            lines = [f"🧠 **Here is everything I remember about you ({officer}):**\n"]
            for idx, (k, v) in enumerate(facts.items(), 1):
                lines.append(f"{idx}. **{k.replace('_', ' ').title()}**: `{v}`")
            
            lines.append(f"\n💡 *You can tell me to remember new details, update any item, or say 'Clear my memory' anytime.*")
            return "\n".join(lines)

        elif intent == "QUERY_SPECIFIC_FACT":
            target_key = meta["fact_key"].lower().replace("_", " ")
            facts = self.get_user_facts(u_key, db=db)
            
            # Look for exact, partial, or token overlap key match
            matched_val = None
            matched_key = None
            target_words = set(target_key.split())

            for k, v in facts.items():
                k_clean = k.lower().replace("_", " ")
                k_words = set(k_clean.split())
                if target_key in k_clean or k_clean in target_key or (target_words & k_words):
                    matched_key = k
                    matched_val = v
                    break
            
            if matched_val:
                return f"🧠 **According to my memory:**\nYour **{matched_key.replace('_', ' ').title()}** is `{matched_val}`."
            else:
                return (
                    f"I don't have a recorded memory for `{target_key}` yet.\n"
                    f"You can tell me: *\"Remember that my {target_key} is [value]\"* and I will save it!"
                )

        elif intent == "SUMMARIZE_CONVERSATION":
            if not conversation_history or len(conversation_history) < 2:
                return "Our conversation just started! As we discuss tenders, bidders, and statutory rules, I will maintain a continuous multi-turn memory for you."
            
            user_msgs = [h.get("text", "") for h in conversation_history if h.get("sender") == "user"]
            lines = [
                f"📜 **Executive Conversation Summary ({len(conversation_history)} total messages):**\n",
                f"• **Active Participant**: {officer} ({user_role})",
                f"• **Topics Discussed ({len(user_msgs)} user queries):**"
            ]
            for idx, m in enumerate(user_msgs, 1):
                lines.append(f"  {idx}. {m[:80]}{'...' if len(m) > 80 else ''}")
            
            lines.append(
                f"\n• **Evaluation Focus**: Statutory compliance verification, 13-node gateway checks, document intelligence, and GFR 2017 rules."
            )
            return "\n".join(lines)

        elif intent == "CLEAR_ALL_FACTS":
            self.clear_user_facts(u_key, db=db)
            return f"🧹 **Memory Cleared!** All personalized facts and preferences for {officer} have been removed from my memory."

        elif intent == "FORGET_SPECIFIC_FACT":
            f_key = meta["fact_key"]
            self.delete_user_fact(u_key, f_key, db=db)
            return f"🧹 **Fact Forgotten:** I have removed `{f_key.replace('_', ' ')}` from your memory."

        return None

    # --------------------------------------------------
    # 4. CONTEXT INJECTION HELPER FOR PROMPTS
    # --------------------------------------------------
    def get_user_memory_context(self, user_key: str, db: Optional[Session] = None) -> str:
        """Returns formatted string of known user facts for LLM prompt injection."""
        facts = self.get_user_facts(user_key, db=db)
        if not facts:
            return ""
        
        lines = ["SAVED USER FACTS & PERSISTENT MEMORY:"]
        for k, v in facts.items():
            lines.append(f"- {k.replace('_', ' ').title()}: {v}")
        return "\n".join(lines)

    # --------------------------------------------------
    # 5. LEGACY INTERACTION SAVING (BACKWARD COMPATIBLE)
    # --------------------------------------------------
    def save_learned_interaction(self, question: str, answer: str, source: str = "INTERACTION"):
        """Saves general Q&A pairs for knowledge retrieval."""
        if not question or not answer:
            return

        clean_q = question.strip()
        clean_a = answer.strip()

        for item in self.memory_store[-10:]:
            if item.get("question", "").lower() == clean_q.lower():
                return

        record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "question": clean_q,
            "answer": clean_a,
            "source": source
        }
        self.memory_store.append(record)
        self._save_json(self.memory_file, self.memory_store)

    def retrieve_relevant_memory(self, query: str, limit: int = 3) -> str:
        if not self.memory_store:
            return ""

        q_words = set(query.lower().split())
        matched = []

        for item in reversed(self.memory_store):
            stored_q = item.get("question", "").lower()
            stored_a = item.get("answer", "")
            
            overlap = sum(1 for w in q_words if w in stored_q or w in stored_a.lower())
            if overlap > 0:
                matched.append(f"Past Question: {item['question']}\nLearned Answer: {item['answer']}")
                if len(matched) >= limit:
                    break

        if matched:
            return "\n\n".join(matched)
        return ""

