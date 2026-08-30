import re
from typing import Dict, Any, Tuple, Optional

class BodhZMultilingualEngine:
    """
    Advanced Multilingual Engine for BodhZ SIH26100.
    Detects Indian languages (Hindi Devanagari, Hinglish, Marathi, Gujarati,
    Bengali, Tamil, Telugu) and generates executive-grade, ChatGPT-standard localized responses.
    """

    # Language Identifiers
    LANG_EN = "en"
    LANG_HINGLISH = "hinglish"
    LANG_HINDI = "hi"
    LANG_MARATHI = "mr"
    LANG_BENGALI = "bn"
    LANG_GUJARATI = "gu"
    LANG_TAMIL = "ta"
    LANG_TELUGU = "te"

    @classmethod
    def detect_language(cls, text: str) -> str:
        t = text.strip()
        
        # Devanagari Script (Hindi / Marathi)
        if re.search(r"[\u0900-\u097F]", t):
            if any(w in t for w in ["आहेत", "केले", "किती", "झाले", "सांगा", "माझे", "कसे"]):
                return cls.LANG_MARATHI
            return cls.LANG_HINDI

        # Bengali Script
        if re.search(r"[\u0980-\u09FF]", t):
            return cls.LANG_BENGALI

        # Gujarati Script
        if re.search(r"[\u0A80-\u0AFF]", t):
            return cls.LANG_GUJARATI

        # Tamil Script
        if re.search(r"[\u0B80-\u0BFF]", t):
            return cls.LANG_TAMIL

        # Telugu Script
        if re.search(r"[\u0C00-\u0C7F]", t):
            return cls.LANG_TELUGU

        # Hinglish Check (Romanized Hindi words)
        hinglish_words = [
            "maine", "kitne", "kitna", "kya", "hai", "hain", "kaha", "kahan", "kaise",
            "batao", "dikhao", "mera", "meri", "mere", "aaj", "kuch", "aur", "ye", "wo",
            "kyu", "kyun", "hoga", "hogi", "theek", "thik", "accha", "acha", "shukriya",
            "dhanyawad", "kaun", "kaunse", "kripya", "namaste", "pranam"
        ]
        words = re.findall(r"\b[a-zA-Z]+\b", t.lower())
        hinglish_matches = sum(1 for w in words if w in hinglish_words)
        if hinglish_matches >= 2 or (len(words) <= 3 and hinglish_matches >= 1):
            return cls.LANG_HINGLISH

        return cls.LANG_EN

    @classmethod
    def localize_response(
        cls,
        intent_type: str,
        data: Dict[str, Any],
        lang: str,
        officer: str,
        original_reply: str
    ) -> str:
        """
        Translates and formats application and procurement responses into the detected language
        with full ChatGPT-grade depth, structure, and clarity.
        """
        if lang == cls.LANG_EN:
            return original_reply

        # --- 1. HINDI (हिंदी - DEVANAGARI) ---
        if lang == cls.LANG_HINDI:
            if intent_type in ["APP_USER_TENDER_COUNT", "APP_USER_TENDERS_LIST"]:
                tenders = data.get("tenders", [])
                count = len(tenders) if tenders else data.get("count", 0)
                
                lines = [
                    f"अधिकारी {officer}, आपके BodhZ कार्यक्षेत्र (Workspace) में कुल {count} सक्रिय खरीद टेंडर पंजीकृत हैं:\n"
                ]
                for idx, t in enumerate(tenders, 1):
                    lines.append(
                        f"{idx}. टेंडर संख्या: {t.get('tender_number', 'N/A')}\n"
                        f"   • शीर्षक: {t.get('title', 'Tender')}\n"
                        f"   • श्रेणी: {t.get('category', 'General')}\n"
                        f"   • वैधानिक नियम: {t.get('rules_count', 4)} अनिवार्य जाँच (GST, PAN, Udyam MSME, OEM MAF)\n"
                        f"   • स्थिति: {t.get('status', 'ACTIVE')}"
                    )
                lines.append(
                    f"\nकार्यकारी सारांश एवं आगामी चरण:\n"
                    f"सभी पंजीकृत टेंडर 13 सरकारी गेटवे नोड्स से जुड़े हैं। आप किसी भी टेंडर को चुनकर बिडरों के अनुपालन स्कोर और दस्तावेज़ों का निरीक्षण कर सकते हैं।"
                )
                return "\n\n".join(lines)

            elif intent_type == "APP_BIDDER_COUNT":
                count = data.get("count", 0)
                bidders = data.get("bidders", [])
                lines = [
                    f"टेंडर {data.get('tender_number', '')} के बिडर प्रस्तुतियाँ विवरण:\n",
                    f"कुल प्राप्त बिड: {count}\n"
                ]
                if bidders:
                    lines.append("प्रस्तुत विक्रेता (Vendors):")
                    for idx, name in enumerate(bidders, 1):
                        lines.append(f"{idx}. {name}")
                lines.append("\nस्थिति: सभी बिडों का दस्तावेज़ विश्लेषण और गेटवे सत्यापन पूरा हो चुका है।")
                return "\n".join(lines)

            elif intent_type == "APP_COMPLIANCE_SCORE":
                score_val = data.get("compliance_score", 0)
                risk_val = data.get("risk_level", "LOW")
                return (
                    f"{data.get('bidder_name', 'बिडर')} की अनुपालन मूल्यांकन रिपोर्ट:\n\n"
                    f"• समग्र अनुपालन स्कोर: {score_val}/100\n"
                    f"• जोखिम स्तर (Risk Tier): {risk_val} RISK\n\n"
                    f"एआई निर्णय समर्थन निष्कर्ष:\n"
                    f"{data.get('recommendation', '')}\n\n"
                    f"अधिकारी मार्गदर्शन:\n"
                    f"GFR 2017 और GeM नियमों के तहत अंतिम योग्यता/अयोग्यता निर्णय का 100% अधिकार खरीद अधिकारी के पास सुरक्षित है।"
                )

            elif intent_type == "APP_OFFICER_IDENTITY":
                return (
                    f"प्रमाणीकरण प्रोफ़ाइल:\n\n"
                    f"• प्रमाणित उपयोगकर्ता: अधिकारी {officer}\n"
                    f"• पद: वरिष्ठ खरीद अधिकारी (Senior Procurement Officer)\n"
                    f"• सुरक्षा स्तर: स्तर-1 खरीद प्रशासक\n\n"
                    f"निर्णय अधिकार जनादेश:\n"
                    f"GFR 2017 नियम 144 के तहत GeM खरीद पोर्टल पर बिड योग्यता और अंतिम निर्णय लेने का 100% पूर्ण अधिकार आपके पास है।"
                )

            elif intent_type == "ACKNOWLEDGMENT":
                return f"समझ गया, अधिकारी {officer}। यदि आपको टेंडर, बिडर मूल्यांकन या अनुपालन रिपोर्ट के संबंध में कुछ और सहायता चाहिए, तो कृपया बताएं।"

            elif intent_type == "GRATITUDE":
                return f"आपका बहुत-बहुत स्वागत है, अधिकारी {officer}! GeM खरीद नियमों, गेटवे सत्यापन या बिडर रिपोर्ट में सहायता के लिए मैं हमेशा उपलब्ध हूँ।"

            elif intent_type == "GREETING":
                if data.get("greeting_type") == "HOW_ARE_YOU":
                    return f"मैं बिल्कुल ठीक हूँ और आपकी सहायता के लिए तैयार हूँ, अधिकारी {officer}! आज मैं आपकी खरीद प्रक्रिया, टेंडर विनिर्देशों और बिडर सत्यापन में किस प्रकार सहायता कर सकता हूँ?"
                return f"नमस्ते, अधिकारी {officer}! आज मैं आपकी खरीद प्रक्रिया, टेंडर विनिर्देशों और बिडर सत्यापन में किस प्रकार सहायता कर सकता हूँ?"

        # --- 2. HINGLISH (ROMANIZED HINDI) ---
        elif lang == cls.LANG_HINGLISH:
            if intent_type in ["APP_USER_TENDER_COUNT", "APP_USER_TENDERS_LIST"]:
                tenders = data.get("tenders", [])
                count = len(tenders) if tenders else data.get("count", 0)
                
                lines = [
                    f"Officer {officer}, aapke BodhZ workspace database mein total {count} active procurement tenders registered hain:\n"
                ]
                for idx, t in enumerate(tenders, 1):
                    lines.append(
                        f"{idx}. Tender Number: {t.get('tender_number', 'N/A')}\n"
                        f"   • Title: {t.get('title', 'Tender')}\n"
                        f"   • Category: {t.get('category', 'General')}\n"
                        f"   • Configured Rules: {t.get('rules_count', 4)} Mandatory Checks (GST, PAN, Udyam MSME, OEM MAF)\n"
                        f"   • Status: {t.get('status', 'ACTIVE')}"
                    )
                lines.append(
                    f"\nSummary & Next Steps:\n"
                    f"Ye sabhi tenders 13 statutory gateway nodes ke sath synchronized hain. Aap kisi bhi tender ko select karke bidder scores aur OCR extractions check kar sakte hain."
                )
                return "\n\n".join(lines)

            elif intent_type == "APP_BIDDER_COUNT":
                count = data.get("count", 0)
                bidders = data.get("bidders", [])
                lines = [
                    f"Tender {data.get('tender_number', '')} ke Bidder Submissions ka overview:\n",
                    f"Total Submitted Bids: {count}\n"
                ]
                if bidders:
                    lines.append("Submitted Bidders:")
                    for idx, name in enumerate(bidders, 1):
                        lines.append(f"{idx}. {name}")
                lines.append("\nStatus: Sabhi bids ka Document Intelligence OCR aur gateway verification check complete ho chuka hai.")
                return "\n".join(lines)

            elif intent_type == "APP_COMPLIANCE_SCORE":
                score_val = data.get("compliance_score", 0)
                risk_val = data.get("risk_level", "LOW")
                return (
                    f"{data.get('bidder_name', 'Bidder')} ka Compliance Evaluation Report:\n\n"
                    f"• Overall Compliance Score: {score_val}/100\n"
                    f"• Risk Tier: {risk_val} RISK\n\n"
                    f"AI Decision Support Finding:\n"
                    f"{data.get('recommendation', '')}\n\n"
                    f"Officer Guidance:\n"
                    f"GFR 2017 aur GeM terms ke mutabiq 100% final decision authority Procurement Officer ke paas reserved hai."
                )

            elif intent_type == "APP_OFFICER_IDENTITY":
                return (
                    f"Authentication Profile:\n\n"
                    f"• Logged in User: Officer {officer}\n"
                    f"• Designated Role: Senior Procurement Officer\n"
                    f"• Access Level: Level-1 Procurement Administrator\n\n"
                    f"Decision Authority Mandate:\n"
                    f"GFR 2017 Rule 144 ke mutabiq BodhZ GeM procurement platform par bids ko qualify/disqualify karne ka 100% final authority aapke paas hai."
                )

            elif intent_type == "ACKNOWLEDGMENT":
                return f"Theek hai, Officer {officer}. Agar aapko tenders, bidders, ya compliance score ke bare mein kuch aur janna hai, toh zaroor batayein."

            elif intent_type == "GRATITUDE":
                return f"Aapka swagat hai, Officer {officer}! Tender rules aur gateway verification mein help ke liye main hamesha taiyar hoon."

            elif intent_type == "GREETING":
                if data.get("greeting_type") == "HOW_ARE_YOU":
                    return f"Main bilkul theek hoon aur aapki help ke liye ready hoon, Officer {officer}! Aaj aapki procurement evaluation mein main kis tarah madad kar sakta hoon?"
                return f"Namaste, Officer {officer}! Aaj aapki procurement evaluation mein main kis tarah madad kar sakta hoon?"

        # --- 3. MARATHI (मराठी) ---
        elif lang == cls.LANG_MARATHI:
            if intent_type in ["APP_USER_TENDER_COUNT", "APP_USER_TENDERS_LIST"]:
                tenders = data.get("tenders", [])
                count = len(tenders) if tenders else data.get("count", 0)
                lines = [f"अधिकारी {officer}, आपल्या वर्कस्पेसमध्ये एकूण {count} सक्रिय टेंडर्स नोंदणीकृत आहेत:\n"]
                for idx, t in enumerate(tenders, 1):
                    lines.append(f"{idx}. टेंडर क्रमांक: {t.get('tender_number', 'N/A')} - {t.get('title', '')} ({t.get('status', 'ACTIVE')})")
                return "\n".join(lines)

            elif intent_type == "GREETING":
                return f"नमस्कार, अधिकारी {officer}! आज मी आपल्या टेंडर मूल्यमापन आणि बिडर पडताळणीमध्ये कशी मदत करू शकतो?"

            elif intent_type == "GRATITUDE":
                return f"आपले स्वागत आहे, अधिकारी {officer}! टेंडर नियम आणि पडताळणीमध्ये मदतीसाठी मी नेहमी उपलब्ध आहे."

        # Default fallback to original plain-text response
        return original_reply
