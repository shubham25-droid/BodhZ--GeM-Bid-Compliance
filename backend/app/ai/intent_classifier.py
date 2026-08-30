import re
from typing import Dict, Any, Optional, List
from app.ai.query_normalizer import BodhZQueryNormalizer

class BodhZIntentType:
    # 1. APPLICATION DATABASE INTENTS
    APP_USER_TENDER_COUNT = "APP_USER_TENDER_COUNT"
    APP_USER_TENDERS_LIST = "APP_USER_TENDERS_LIST"
    APP_CURRENT_TENDER = "APP_CURRENT_TENDER"
    APP_TENDER_REQUIREMENTS = "APP_TENDER_REQUIREMENTS"
    APP_BIDDER_COUNT = "APP_BIDDER_COUNT"
    APP_BIDDER_DETAILS = "APP_BIDDER_DETAILS"
    APP_BIDDER_DOCUMENTS = "APP_BIDDER_DOCUMENTS"
    APP_MISSING_DOCUMENTS = "APP_MISSING_DOCUMENTS"
    APP_VERIFICATION_RESULTS = "APP_VERIFICATION_RESULTS"
    APP_COMPLIANCE_FINDINGS = "APP_COMPLIANCE_FINDINGS"
    APP_COMPLIANCE_SCORE = "APP_COMPLIANCE_SCORE"
    APP_RISK_ASSESSMENT = "APP_RISK_ASSESSMENT"
    APP_REPORTS = "APP_REPORTS"
    APP_TODAY_ACTIVITY = "APP_TODAY_ACTIVITY"
    APP_AUDIT_HISTORY = "APP_AUDIT_HISTORY"
    APP_OFFICER_IDENTITY = "APP_OFFICER_IDENTITY"

    # 2. CONVERSATIONAL & GENERAL INTENTS
    ACKNOWLEDGMENT = "ACKNOWLEDGMENT"
    GRATITUDE = "GRATITUDE"
    CONVERSATION_FOLLOWUP = "CONVERSATION_FOLLOWUP"
    GREETING = "GREETING"
    HINGLISH_CASUAL = "HINGLISH_CASUAL"
    OFFICER_DECISION_MANDATE = "OFFICER_DECISION_MANDATE"
    GENERAL_KNOWLEDGE = "GENERAL_KNOWLEDGE"


class BodhZIntentClassifier:
    """
    High-precision Intent Classifier separating General Knowledge questions
    from Authorized Application Database Queries. Supports multi-turn conversational follow-ups
    and typo-tolerant normalization.
    """

    @staticmethod
    def classify(message: str, conversation_history: Optional[List[Dict[str, str]]] = None) -> Dict[str, Any]:
        raw_msg = message.strip().lower()
        msg = BodhZQueryNormalizer.normalize(raw_msg)

        # Extract last user query from conversation history if available
        last_user_query = ""
        if conversation_history:
            for item in reversed(conversation_history):
                if item.get("sender") == "user" and item.get("text", "").strip().lower() != msg:
                    last_user_query = item.get("text", "").strip().lower()
                    break

        # --- 1. ACKNOWLEDGMENT & CASUAL CONFIRMATIONS ("ok", "ook", "okk", "okay", "got it", "fine", "cool", "done", "understood", "theek h") ---
        if re.search(r"^(?:o+k+|o+k+a+y+|k|alright|got\s*it|fine|cool|done|understood|sure|great|perfect|theek\s*h[ai]*|thik\s*h[ai]*|accha|acha|sahi\s*h[ai]*|ha|haan|hnn|hn)[\.!\s]*$", msg):
            return {"type": BodhZIntentType.ACKNOWLEDGMENT}

        # --- 2. GRATITUDE / THANKS ---
        if re.search(r"^(?:thanks|thank\s*you|dhanyawad|dhanyavad|shukriya|many\s*thanks)[\.!\s]*$", msg):
            return {"type": BodhZIntentType.GRATITUDE}

        # --- 3. CONVERSATION CORRECTION ("sorry, I meant...") ---
        if any(p in msg for p in ["sorry", "i meant", "meaning the previous", "i mean tender", "i mean bid"]):
            return {"type": BodhZIntentType.CONVERSATION_FOLLOWUP}

        # --- 4. ELLIPTICAL MULTI-TURN FOLLOW-UPS ("and bids", "and tenders", "what about bids", "aur bids") ---
        if re.search(r"^(?:and|what about|how about|aur|tell me about)\s+(?:the\s+)?bids?\??$", msg) or msg in ["bids", "bids?", "bidders", "bidders?"]:
            if any(w in last_user_query for w in ["what is", "meaning", "definition", "define", "kya hota", "means"]):
                return {"type": BodhZIntentType.GENERAL_KNOWLEDGE}
            return {"type": BodhZIntentType.APP_BIDDER_COUNT}

        if re.search(r"^(?:and|what about|how about|aur|tell me about)\s+(?:the\s+)?tenders?\??$", msg) or msg in ["tenders", "tenders?", "tender"]:
            if any(w in last_user_query for w in ["what is", "meaning", "definition", "define", "kya hota", "means"]):
                return {"type": BodhZIntentType.GENERAL_KNOWLEDGE}
            return {"type": BodhZIntentType.APP_USER_TENDERS_LIST}

        if re.search(r"^(?:and|what about|how about|aur)\s+(?:the\s+)?score\??$", msg) or msg in ["score", "score?"]:
            return {"type": BodhZIntentType.APP_COMPLIANCE_SCORE}

        if re.search(r"^(?:and|what about|how about|aur)\s+(?:the\s+)?docs?\??$", msg) or "missing" in msg:
            return {"type": BodhZIntentType.APP_MISSING_DOCUMENTS}

        # --- 5. OFFICER IDENTITY / WHO AM I ---
        if any(w in msg for w in ["who am i", "my name", "mera naam", "who is logged in", "current user", "logged in officer"]):
            return {"type": BodhZIntentType.APP_OFFICER_IDENTITY}

        # --- 6. TODAY'S ACTIVITY & AUDIT ---
        if any(w in msg for w in ["today", "aaj"]) and any(w in msg for w in ["upload", "check", "evaluated", "bids", "tenders", "activity"]):
            return {"type": BodhZIntentType.APP_TODAY_ACTIVITY}

        if any(w in msg for w in ["audit history", "audit trail", "audit log", "who evaluated", "verification history", "recent history", "history"]):
            return {"type": BodhZIntentType.APP_AUDIT_HISTORY}

        # --- 7. TENDER INVENTORY & COUNT QUERIES ---
        if any(w in msg for w in ["how many tender", "how many tenders", "tender count", "total tenders", "number of tenders", "tenders uploaded", "tenders i had uploaded", "tenders uploaded by me"]):
            return {"type": BodhZIntentType.APP_USER_TENDER_COUNT}

        if any(w in msg for w in ["show my tenders", "list my tenders", "show tenders", "list tenders", "all tenders", "my tenders", "tenders list"]):
            return {"type": BodhZIntentType.APP_USER_TENDERS_LIST}

        if any(w in msg for w in ["what is my current tender", "my active tender", "current tender", "this tender", "when did i upload this tender", "active tender details"]):
            return {"type": BodhZIntentType.APP_CURRENT_TENDER}

        if any(w in msg for w in ["tender rules", "tender requirements", "rules for this tender", "mandatory rules", "configured rules"]):
            return {"type": BodhZIntentType.APP_TENDER_REQUIREMENTS}

        # --- 8. BIDDER INVENTORY & BIDDER DETAILS ---
        if any(w in msg for w in ["how many bidder", "how many bidders", "bidder count", "how many bids", "total bids", "bids count", "bids evaluated", "bids i have"]):
            return {"type": BodhZIntentType.APP_BIDDER_COUNT}

        if any(w in msg for w in ["which bidder did i check", "selected bidder", "active bidder", "this bidder details", "who is the bidder"]):
            return {"type": BodhZIntentType.APP_BIDDER_DETAILS}

        # --- 9. MISSING DOCUMENTS & UPLOADED DOCUMENTS ---
        if any(w in msg for w in ["missing document", "missing documents", "which documents are missing", "any document missing", "document missing", "which doc missing"]):
            return {"type": BodhZIntentType.APP_MISSING_DOCUMENTS}

        if any(w in msg for w in ["what documents were uploaded", "uploaded documents", "bidder documents", "documents uploaded"]):
            return {"type": BodhZIntentType.APP_BIDDER_DOCUMENTS}

        # --- 10. VERIFICATION RESULTS & FINDINGS ---
        if any(w in msg for w in ["verification results", "gateway results", "what checks failed", "failed checks", "verification findings"]):
            return {"type": BodhZIntentType.APP_VERIFICATION_RESULTS}

        if any(w in msg for w in ["compliance findings", "findings list", "what are the findings"]):
            return {"type": BodhZIntentType.APP_COMPLIANCE_FINDINGS}

        # --- 11. REPORTS ---
        if any(w in msg for w in ["show reports", "procurement reports", "evaluation report", "my reports", "show my report"]):
            return {"type": BodhZIntentType.APP_REPORTS}

        # --- 12. COMPLIANCE SCORE & RISK FACTORS ---
        if any(w in msg for w in ["score", "compliance score", "bidder score", "marks", "points"]):
            return {"type": BodhZIntentType.APP_COMPLIANCE_SCORE}

        if any(w in msg for w in ["why is this bidder high risk", "why high risk", "why critical", "risk factors", "why disqualified", "why flagged", "risk assessment"]):
            return {"type": BodhZIntentType.APP_RISK_ASSESSMENT}

        # --- 13. GREETINGS & CASUAL INQUIRIES ---
        if any(w in msg for w in ["how are you", "how r u", "how are u", "how do you do", "kaise ho", "kese ho", "kya haal", "whats up", "what's up", "wassup"]):
            return {"type": BodhZIntentType.GREETING, "greeting_phrase": "HOW_ARE_YOU"}
        elif re.search(r"\b(good\s*morning|gm)\b", msg):
            return {"type": BodhZIntentType.GREETING, "greeting_phrase": "Good morning"}
        elif re.search(r"\b(good\s*afternoon|ga)\b", msg):
            return {"type": BodhZIntentType.GREETING, "greeting_phrase": "Good afternoon"}
        elif re.search(r"\b(good\s*evening|ge)\b", msg):
            return {"type": BodhZIntentType.GREETING, "greeting_phrase": "Good evening"}
        elif re.search(r"\b(namaste|namaskar|pranam)\b", msg):
            return {"type": BodhZIntentType.GREETING, "greeting_phrase": "Namaste"}
        elif re.search(r"\b(h+e+l+l*o+|h+i+|h+e+y+|salute|greetings|hola)\b", msg):
            return {"type": BodhZIntentType.GREETING, "greeting_phrase": "Hello"}

        # --- 14. OFFICER AUTHORITY MANDATE ---
        if any(phrase in msg for phrase in ["can ai disqualify", "can ai reject", "disqualify a bidder", "who makes final decision", "can ai decide", "reject a bidder"]):
            return {"type": BodhZIntentType.OFFICER_DECISION_MANDATE}

        # --- 15. HINGLISH CASUAL ---
        if any(phrase in msg for phrase in ["kya bol raha", "kya bol rahe", "kaha h", "kahan h", "samajh nahi", "kya hai ye", "kya h ye"]):
            return {"type": BodhZIntentType.HINGLISH_CASUAL}

        # --- 16. GENERAL KNOWLEDGE (Default for conceptual questions) ---
        return {"type": BodhZIntentType.GENERAL_KNOWLEDGE}
