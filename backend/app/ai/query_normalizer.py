import re
from typing import Optional

class BodhZQueryNormalizer:
    """
    Advanced text normalizer correcting typos, slang, abbreviations,
    Hinglish, Hindi (Devanagari), and regional language queries before intent classification.
    Also provides subtle typo detection suggestions.
    """

    SUBSTITUTIONS = [
        # Hindi Devanagari Mappings
        (r"कितने\s+टेंडर|टेंडर\s+संख्या|टेंडर\s+दिखाओ|किती\s+टेंडर", "how many tenders"),
        (r"कितने\s+बिडर|बिडर\s+संख्या|किती\s+बिडर", "how many bidders"),
        (r"स्कोर|स्कोअर|अंक\s+क्या\s+है|गुण\s+काय\s+आहे|नंबर", "what is score"),
        (r"दस्तावेज|दस्तावेज़|कागदपत्रे", "documents"),
        (r"मैं\s+कौन\s+हूँ|मेरा\s+नाम|मी\s+कोण\s+आहे", "who am i"),
        (r"नमस्ते|प्रणाम|शुभ\s+प्रभात|नमस्कार", "hello"),
        (r"धन्यवाद|शुक्रिया|आभार", "thanks"),
        # Greeting normalizations
        (r"\b(?:how\s*r\s*u|how\s*are\s*u|how\s*are\s*you|hw\s*r\s*u|kaise\s*ho|kese\s*ho|kya\s*haal|whats\s*up|wassup)\b", "how are you"),

        # Short question normalizations
        (r"^bid\s+(?:means?|kya\s+hota\s+hai|kya\s+h)\??$", "what is a bid"),
        (r"^tender\s+(?:means?|kya\s+hota\s+hai|kya\s+h)\??$", "what is a tender"),
        (r"^gst\??$", "what is gst"),
        (r"^udyam\??$", "what is udyam msme"),
        (r"^oem\??$", "what is oem authorization"),
        (r"^emd\??$", "what is emd"),
        (r"^blacklisting\??$", "what is blacklisting debarment"),
        (r"^risk\??$", "what is bidder risk"),
        (r"^score\??$", "what is compliance score"),
        (r"^report\??$", "show procurement reports"),
        (r"^reports\??$", "show procurement reports"),

        # Hinglish & Casual Hindi
        (r"\b(?:maine|mene|mere)\s+(?:kitne|kitte)\s+(?:tender|tenders)\b", "how many tenders"),
        (r"\b(?:mere|sab)\s+(?:tenders?)\s+(?:dikhao|batao|list)\b", "show my tenders"),
        (r"\b(?:kitne|kitte)\s+(?:bidders?|bids)\s+(?:hai|hain|h)\b", "how many bidders"),
        (r"\b(?:is|iss)\s+(?:bidder|bider)\s+ka\s+(?:score|marks|point)\b", "what is score"),
        (r"\b(?:kaun|kon|kaunse|konse)\s+(?:se\s+)?(?:docs|documnts|dastavez|document)\s+(?:missing|gayab)\b", "missing documents"),
        (r"\b(?:which\s+)?(?:docs?|documnts?)\s+missing\b", "missing documents"),
        (r"\b(?:kyu|kyun)\s+(?:reject|fail|disqualif|risk)\s+hua\b", "why is this bidder high risk"),
        (r"\b(?:aaj|today)\s+(?:kya|kitne)\s+(?:upload|check|kiya|kiye)\b", "what did i upload today"),
        (r"\b(?:mai|main|hum)\s+(?:kaun|kon)\s+(?:hu|hoon|h)\b", "who am i"),

        # Reject / Disqualify AI queries
        (r"\b(?:can\s+ai\s+reject|can\s+ai\s+disqualify|can\s+ai\s+decide|reject\s+bidder)\b", "can ai disqualify a bidder"),

        # Quantity & Questions
        (r"\b(?:mny|mani|manyy)\b", "many"),
        (r"\b(?:abt|bout)\b", "about"),
        (r"\b(?:b/w|betwen|btwn)\b", "between"),
        (r"\b(?:bcz|coz|cuz)\b", "because"),
        (r"\b(?:whos|whois|who am i|who m i)\b", "who am i"),
        (r"\b(?:wht|wat|kya|kia)\b", "what"),
        (r"\b(?:hw|howw|kaise|kese)\b", "how"),
        (r"\b(?:wn|wen|kab)\b", "when"),
        (r"\b(?:wr|wer|kaha|kahan)\b", "where"),
        (r"\b(?:y|kyu|kyun|why)\b", "why"),
        (r"\b(?:plz|pls|plse|kripya)\b", "please"),
        (r"\b(?:thx|ty|tq|dhanyawad|shukriya|thanks|thank you)\b", "thanks"),
        (r"\b(?:u|ur|aap|tum|mera|meri|my)\b", "my"),
        (r"\b(?:btao|batao|dikhao|dikhaye|tell me|show me)\b", "show"),

        # Tenders & Bids typos
        (r"\b(?:tendr|tendrs|tenderss|tendar|tndr)\b", "tender"),
        (r"\b(?:bider|biders|bidr|biddr|bids|bids\?)\b", "bids"),
        (r"\b(?:documnt|documnts|dokuments|dokumnt|dox|docs)\b", "documents"),
        (r"\b(?:complience|compliencee|complaince|complince)\b", "compliance"),
        (r"\b(?:scrore|scor|scorre|point|marks)\b", "score"),
        (r"\b(?:autherization|authorisation|authrization|authrizaton|maf|oem auth)\b", "oem authorization"),
        (r"\b(?:cancle|cancl|disqualif|rejct|reject)\b", "disqualification"),
        (r"\b(?:diff|diffrnce|diffrence|deference)\b", "difference"),
        (r"\b(?:verificaton|verfication|verifcation|varification)\b", "verification"),
        
        # Government terminology
        (r"\b(?:g\s*e\s*m|gem portal|gem gov in)\b", "gem"),
        (r"\b(?:g\s*f\s*r|gfr 2017|gfr rules)\b", "gfr"),
        (r"\b(?:gst|gstn|g s t)\b", "gst"),
        (r"\b(?:msme|udyam|udyam aadhar|uam)\b", "udyam"),
        (r"\b(?:mii|make in india|pmi)\b", "make in india"),
        (r"\b(?:epbg|pbg|performance security|bank guarantee)\b", "epbg"),
        (r"\b(?:emd|earnest money|bid security)\b", "emd")
    ]

    @classmethod
    def normalize(cls, text: str) -> str:
        if not text:
            return ""
        
        cleaned = text.strip().lower()

        # Remove excessive repeated characters (e.g., 'heeeey' -> 'hey', 'sooo' -> 'so', 'okkkk' -> 'ok')
        cleaned = re.sub(r"(.)\1{2,}", r"\1\1", cleaned)

        # Apply specific procurement domain substitutions
        for pattern, replacement in cls.SUBSTITUTIONS:
            cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)

        return cleaned

    @classmethod
    def detect_typo_correction(cls, raw_text: str) -> Optional[str]:
        """
        Detects obvious spelling/grammar mistakes and returns a subtle correction prompt.
        Only returns if the user text actually contains a typo or mangled grammar.
        """
        t = raw_text.strip().lower()
        if not t:
            return None

        # Typo: uploded / uplod / how many tender i upload
        if "uploded" in t or "uplod" in t or "how many tender i upload" in t:
            if "how many tenders have i uploaded" not in t:
                return "How many tenders have I uploaded?"

        # Typo: verificaton / verfication / varification
        if "verificaton" in t or "verfication" in t or "varification" in t:
            if "gst" in t:
                return "GST verification"
            if "udyam" in t:
                return "Udyam verification"

        # Typo: which doc missing / documnt missing
        if "which doc missing" in t or "documnt missing" in t:
            return "Which documents are missing?"

        # Typo: bider / scrore / scor
        if "scrore" in t or "bider" in t or "bidr" in t:
            if "score" in t or "scrore" in t or "scor" in t:
                return "What is this bidder's compliance score?"

        return None
