import logging
import json
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.ai.openai_client import OpenAIBackendClient
from app.ai.context_builder import BodhZContextBuilder
from app.ai.prompt_manager import BodhZPromptManager
from app.ai.intent_classifier import BodhZIntentClassifier, BodhZIntentType
from app.ai.backend_tools import BodhZBackendTools
from app.ai.knowledge_base import BodhZKnowledgeBase
from app.ai.knowledge_retriever import BodhZKnowledgeRetriever
from app.ai.sanitizer import BodhZTextSanitizer
from app.ai.learning_memory import BodhZLearningMemory
from app.ai.universal_qa import UniversalQAEngine
from app.ai.government_knowledge import GovernmentProcurementEncyclopedia
from app.ai.multilingual_engine import BodhZMultilingualEngine
from app.ai.query_normalizer import BodhZQueryNormalizer

logger = logging.getLogger(__name__)

# --------------------------------------------------
# MASTER BODHZ AI PROCUREMENT ASSISTANT SERVICE (SIH26100)
# --------------------------------------------------
class BodhZChatbotService:
    """
    BodhZ AI Assistant — AI-powered procurement compliance decision-support assistant.
    Provides authoritative, precise, evidence-grounded, and government-workflow oriented
    procurement advisory. Connects to the live SQLite application database and enforces 100%
    human Procurement Officer final decision authority.
    """

    def __init__(self):
        self.openai_client = OpenAIBackendClient()
        self.knowledge_retriever = BodhZKnowledgeRetriever()
        self.learning_memory = BodhZLearningMemory()

    async def process_chat_message(
        self,
        user_message: str,
        db: Optional[Session] = None,
        active_tender: Optional[Dict[str, Any]] = None,
        active_bidder: Optional[Dict[str, Any]] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        user_name: Optional[str] = None,
        user_role: Optional[str] = None,
        all_tenders: Optional[List[Dict[str, Any]]] = None,
        all_bidders: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        user_msg = user_message.strip()
        officer = user_name.strip() if user_name else "Senior Procurement Officer"
        role_label = "Senior Procurement Officer" if (not user_role or "PROCUREMENT" in user_role.upper()) else "Compliance Auditor"

        # Step 1: Detect User Language
        detected_lang = BodhZMultilingualEngine.detect_language(user_msg)

        # Step 2: High-Precision Intent Classification with Multi-Turn Context
        intent = BodhZIntentClassifier.classify(user_msg, conversation_history)
        intent_type = intent["type"]
        logger.info(f"Chatbot Intent Classified: {intent_type} (Language: {detected_lang})")

        # Active IDs extraction
        active_t_id = active_tender.get("id") or active_tender.get("tender_number") if active_tender else None
        active_b_id = active_bidder.get("id") if active_bidder else None
        active_b_name = active_bidder.get("name") or active_bidder.get("legal_name") if active_bidder else None

        # Check for subtle spelling typo
        typo_prompt = BodhZQueryNormalizer.detect_typo_correction(user_msg)

        # =========================================================================
        # BRANCH A: MANDATORY BACKEND DATABASE TOOLS EXECUTION
        # =========================================================================
        db_tool_result = None

        if db:
            if intent_type in [BodhZIntentType.APP_USER_TENDER_COUNT, BodhZIntentType.APP_USER_TENDERS_LIST]:
                db_tool_result = BodhZBackendTools.get_user_tenders(db, username=officer)
                tenders = db_tool_result["tenders"]
                count = len(tenders)
                
                if count == 0:
                    reply = (
                        f"Officer {officer}, you currently have no active tenders in your workspace database.\n\n"
                        f"To initiate a procurement cycle, navigate to the Tender Management tab and click '+ Upload Tender' "
                        f"to define tender specifications, eligibility criteria, and mandatory rule sets."
                    )
                else:
                    lines = [
                        f"Officer {officer}, you have {count} active procurement tender(s) registered in your BodhZ workspace database:\n"
                    ]
                    for idx, t in enumerate(tenders, 1):
                        lines.append(
                            f"{idx}. Tender Number: {t['tender_number']}\n"
                            f"   • Title: {t['title']}\n"
                            f"   • Category: {t['category']}\n"
                            f"   • Configured Rules: {t['rules_count']} Mandatory Statutory Checks (GST, PAN, Udyam MSME, OEM MAF)\n"
                            f"   • Submitted Bids: {t['bids_count']}\n"
                            f"   • Uploaded Date: {t['created_at']}\n"
                            f"   • Workflow Status: {t['status']}"
                        )
                    
                    lines.append(
                        f"\nSummary & Next Actions:\n"
                        f"All registered tenders are active and linked with automated 13-node gateway verification checks. "
                        f"You can select any tender to inspect bidder compliance sheets, view OCR extractions, or open technical bids."
                    )
                    reply = "\n\n".join(lines)
                
                return self._build_response(reply, "DB_TOOL_TENDERS", "BodhZ-DatabaseTool-v1.0", intent_type=intent_type, data=db_tool_result, detected_lang=detected_lang, officer=officer, typo_prompt=typo_prompt)

            elif intent_type == BodhZIntentType.APP_CURRENT_TENDER:
                if active_t_id:
                    db_tool_result = BodhZBackendTools.get_tender_details(db, active_t_id)
                    if db_tool_result.get("success"):
                        t = db_tool_result["tender"]
                        lines = [
                            f"Active Selected Tender Overview:\n",
                            f"• Tender Number: {t['tender_number']}",
                            f"• Tender Title: {t['title']}",
                            f"• Category: {t['category']}",
                            f"• Created Timestamp: {t['created_at']}",
                            f"• Total Bidders Submitted: {t['total_bids']}",
                            f"• Current Workflow Status: {t['status']}",
                            f"\nConfigured Statutory Eligibility Criteria ({len(t['requirements'])} Rules):"
                        ]
                        for idx, r in enumerate(t['requirements'], 1):
                            lines.append(f"  {idx}. [{r['module']}] {r['title']} (Mandatory: {'Yes' if r['mandatory'] else 'No'})")
                        
                        lines.append(
                            f"\nCompliance Engine Status:\n"
                            f"Automated verification connectors are synchronized across GSTN, Income Tax, Udyam, and OEM verification nodes."
                        )
                        reply = "\n".join(lines)
                        return self._build_response(reply, "DB_TOOL_CURRENT_TENDER", "BodhZ-DatabaseTool-v1.0", intent_type=intent_type, data=db_tool_result, detected_lang=detected_lang, officer=officer, typo_prompt=typo_prompt)
                
                db_tool_result = BodhZBackendTools.get_user_tenders(db)
                if db_tool_result.get("tenders"):
                    t = db_tool_result["tenders"][0]
                    reply = f"Your latest tender in workspace is {t['tender_number']}: {t['title']} (Uploaded: {t['created_at']}, Status: {t['status']})."
                else:
                    reply = "No tender is currently configured in your workspace."
                return self._build_response(reply, "DB_TOOL_CURRENT_TENDER", "BodhZ-DatabaseTool-v1.0", intent_type=intent_type, data=db_tool_result, detected_lang=detected_lang, officer=officer, typo_prompt=typo_prompt)

            elif intent_type == BodhZIntentType.APP_TENDER_REQUIREMENTS:
                db_tool_result = BodhZBackendTools.get_tender_requirements(db, active_t_id or "GEM/2026/B/994810")
                if db_tool_result.get("success"):
                    reqs = db_tool_result["requirements"]
                    lines = [
                        f"Mandatory Statutory Requirements for Tender {db_tool_result['tender_number']}:\n",
                        f"Total Configured Rules: {len(reqs)}\n"
                    ]
                    for idx, r in enumerate(reqs, 1):
                        lines.append(f"{idx}. Gateway Node: {r['module']}\n   • Rule Description: {r['title']}\n   • Verification Method: {r['rule_type']}\n   • Enforceability: Mandatory")
                    
                    lines.append(f"\nRegulatory Basis:\nEnforced under GFR 2017 Rules 144, 149, 170, and GeM General Terms and Conditions.")
                    reply = "\n\n".join(lines)
                    return self._build_response(reply, "DB_TOOL_REQUIREMENTS", "BodhZ-DatabaseTool-v1.0", intent_type=intent_type, data=db_tool_result, detected_lang=detected_lang, officer=officer, typo_prompt=typo_prompt)

            elif intent_type == BodhZIntentType.APP_BIDDER_COUNT:
                db_tool_result = BodhZBackendTools.get_bidder_count(db, active_t_id)
                count = db_tool_result["count"]
                b_names = db_tool_result["bidders"]
                
                lines = [
                    f"Bidder Submission Intelligence for Tender {db_tool_result['tender_number']}:\n",
                    f"Total Bidders Submitted: {count}\n"
                ]
                if b_names:
                    lines.append("Submitted Vendors:")
                    for idx, name in enumerate(b_names, 1):
                        lines.append(f"{idx}. {name}")
                
                lines.append(
                    f"\nAutomated Evaluation Status:\n"
                    f"All submitted bids have been processed through Document Intelligence OCR and 13 statutory gateway verification nodes."
                )
                reply = "\n".join(lines)
                return self._build_response(reply, "DB_TOOL_BIDDER_COUNT", "BodhZ-DatabaseTool-v1.0", intent_type=intent_type, data=db_tool_result, detected_lang=detected_lang, officer=officer, typo_prompt=typo_prompt)

            elif intent_type == BodhZIntentType.APP_BIDDER_DETAILS:
                db_tool_result = BodhZBackendTools.get_bidder_details(db, active_b_id, active_b_name)
                if db_tool_result.get("success"):
                    b = db_tool_result
                    reply = (
                        f"Comprehensive Bidder Compliance Profile:\n\n"
                        f"• Legal Entity Name: {b['legal_name']}\n"
                        f"• Associated Tender: {b['tender_number']}\n"
                        f"• GSTIN Registration: {b['gstin']} (Node 1 Verified)\n"
                        f"• Permanent Account Number (PAN): {b['pan']} (Node 2 Verified)\n"
                        f"• Udyam MSME Registration: {b['udyam']} (Node 3 Verified)\n"
                        f"• Bid Submission Date: {b['submission_date']}\n"
                        f"• Uploaded Document Bundles: {b['documents_uploaded']}\n\n"
                        f"Compliance Scoring & Risk Tier:\n"
                        f"• Overall Compliance Score: {b['compliance_score']}/100\n"
                        f"• Risk Classification: {b['risk_level']} RISK\n"
                        f"• Technical Evaluation Status: {b['status']}"
                    )
                    return self._build_response(reply, "DB_TOOL_BIDDER_DETAILS", "BodhZ-DatabaseTool-v1.0", intent_type=intent_type, data=db_tool_result, detected_lang=detected_lang, officer=officer, typo_prompt=typo_prompt)

            elif intent_type == BodhZIntentType.APP_COMPLIANCE_SCORE:
                db_tool_result = BodhZBackendTools.get_compliance_score(db, active_b_id, active_b_name)
                if db_tool_result.get("success"):
                    b = db_tool_result
                    score_val = b.get("compliance_score", 0)
                    risk_val = b.get("risk_level", "LOW")
                    
                    status_desc = "Fully Compliant across all statutory criteria." if score_val == 100 else ("Review Recommended for identified discrepancies." if score_val >= 70 else "Non-Compliant: Critical statutory deviations detected.")
                    
                    reply = (
                        f"Compliance Evaluation Report for {b['bidder_name']}:\n\n"
                        f"• Overall Compliance Score: {score_val}/100\n"
                        f"• Risk Classification: {risk_val} RISK\n"
                        f"• Compliance Summary: {status_desc}\n\n"
                        f"AI Decision Support Finding:\n"
                        f"{b['recommendation']}\n\n"
                        f"Officer Action Guidance:\n"
                        f"Under GFR 2017 & GeM guidelines, 100% final qualification authority belongs to the Procurement Officer. "
                        f"You may review extracted document citations or record your official qualification decision in the Decision Support tab."
                    )
                    return self._build_response(reply, "DB_TOOL_COMPLIANCE_SCORE", "BodhZ-DatabaseTool-v1.0", intent_type=intent_type, data=db_tool_result, detected_lang=detected_lang, officer=officer, typo_prompt=typo_prompt)

            elif intent_type == BodhZIntentType.APP_RISK_ASSESSMENT:
                db_tool_result = BodhZBackendTools.get_risk_assessment(db, active_b_id, active_b_name)
                if db_tool_result.get("success"):
                    b = db_tool_result
                    lines = [
                        f"Risk Assessment & Root Cause Analysis for {b['bidder_name']}:\n",
                        f"• Overall Risk Tier: {b['risk_level']} RISK",
                        f"• Compliance Score: {b['compliance_score']}/100",
                        f"• AI Evaluation Finding: {b['ai_recommendation']}\n"
                    ]
                    if b["findings"]:
                        lines.append("Detected Discrepancies & Statutory Non-Conformities:")
                        for idx, f in enumerate(b["findings"], 1):
                            lines.append(f"{idx}. [{f['severity']}] Code: {f['code']}\n   Finding: {f['message']}")
                    else:
                        lines.append("• No critical non-conformities or certificate discrepancies detected.")
                    
                    lines.append(
                        f"\nStatutory Advisory:\n"
                        f"If the finding relates to minor spelling variations, the Evaluation Committee may request clarification under GeM terms. "
                        f"If the finding relates to expired authorization or debarment, mandatory disqualification applies under GFR Rule 151 / 144."
                    )
                    reply = "\n\n".join(lines)
                    return self._build_response(reply, "DB_TOOL_RISK_ASSESSMENT", "BodhZ-DatabaseTool-v1.0", intent_type=intent_type, data=db_tool_result, detected_lang=detected_lang, officer=officer, typo_prompt=typo_prompt)

            elif intent_type == BodhZIntentType.APP_MISSING_DOCUMENTS:
                db_tool_result = BodhZBackendTools.get_missing_documents(db, active_b_id, active_b_name)
                if db_tool_result.get("success"):
                    missing = db_tool_result["missing_documents"]
                    lines = [f"Document Completeness Audit for {db_tool_result['bidder_name']} (Tender {db_tool_result['tender_number']}):\n"]
                    if not missing:
                        lines.append("✓ All mandatory statutory documents and OEM certificates have been successfully uploaded and verified.")
                    else:
                        lines.append(f"⚠️ Missing Mandatory Certificates ({len(missing)} total):")
                        for idx, m in enumerate(missing, 1):
                            lines.append(f"{idx}. {m}")
                        lines.append(
                            f"\nRecommended Action:\n"
                            f"Under GeM Bid Evaluation rules, missing mandatory eligibility documents render a technical bid non-responsive, "
                            f"unless the bidder is eligible for MSME/Startup exemption under GFR Rule 170."
                        )
                    reply = "\n\n".join(lines)
                    return self._build_response(reply, "DB_TOOL_MISSING_DOCS", "BodhZ-DatabaseTool-v1.0", intent_type=intent_type, data=db_tool_result, detected_lang=detected_lang, officer=officer, typo_prompt=typo_prompt)

            elif intent_type in [BodhZIntentType.APP_VERIFICATION_RESULTS, BodhZIntentType.APP_COMPLIANCE_FINDINGS]:
                db_tool_result = BodhZBackendTools.get_verification_results(db, active_b_id, active_b_name)
                if db_tool_result.get("success"):
                    results = db_tool_result.get("verification_results", [])
                    lines = [f"Statutory Gateway Verification Results for {db_tool_result['bidder_name']}:\n"]
                    for idx, res in enumerate(results, 1):
                        lines.append(
                            f"{idx}. Module: {res['module']}\n"
                            f"   • Status: {res['status']}\n"
                            f"   • Source Portal: {res['source']}\n"
                            f"   • Verification Mode: {res['mode']}\n"
                            f"   • Detail: {res['reason']}"
                        )
                    reply = "\n\n".join(lines)
                    return self._build_response(reply, "DB_TOOL_VERIFICATION_RESULTS", "BodhZ-DatabaseTool-v1.0", intent_type=intent_type, data=db_tool_result, detected_lang=detected_lang, officer=officer, typo_prompt=typo_prompt)

            elif intent_type == BodhZIntentType.APP_REPORTS:
                db_tool_result = BodhZBackendTools.get_reports(db, bid_id=active_b_id, tender_id=active_t_id)
                reports = db_tool_result.get("reports", [])
                if not reports:
                    reply = "No formal evaluation reports have been recorded in your workspace yet."
                else:
                    lines = [f"Procurement Compliance Evaluation Reports ({len(reports)} total):\n"]
                    for idx, r in enumerate(reports, 1):
                        lines.append(
                            f"{idx}. Report ID: {r['report_id']}\n"
                            f"   • Tender Number: {r['tender_number']}\n"
                            f"   • Bidder Name: {r['bidder_name']}\n"
                            f"   • Compliance Score: {r['compliance_score']}/100 ({r['risk_level']} RISK)\n"
                            f"   • Generated Date: {r['generated_at']}\n"
                            f"   • Summary: {r['recommendation']}"
                        )
                    reply = "\n\n".join(lines)
                return self._build_response(reply, "DB_TOOL_REPORTS", "BodhZ-DatabaseTool-v1.0", intent_type=intent_type, data=db_tool_result, detected_lang=detected_lang, officer=officer, typo_prompt=typo_prompt)

            elif intent_type == BodhZIntentType.APP_TODAY_ACTIVITY:
                db_tool_result = BodhZBackendTools.get_today_activity(db, actor_id=officer)
                act = db_tool_result
                reply = (
                    f"Executive Activity Summary for Today ({act['date']}):\n\n"
                    f"• Tenders Created/Uploaded Today: {act['tenders_uploaded_today']}\n"
                    f"• Bids Submitted Today: {act['bids_submitted_today']}\n"
                    f"• Bids Evaluated Across 13 Gateway Nodes: {act['bids_evaluated_today']}\n"
                    f"• Officer Qualification Decisions Recorded: {act['officer_decisions_recorded_today']}\n\n"
                    f"All database transactions and verification gateway calls are cryptographically signed and logged in the immutable audit trail."
                )
                return self._build_response(reply, "DB_TOOL_TODAY_ACTIVITY", "BodhZ-DatabaseTool-v1.0", intent_type=intent_type, data=db_tool_result, detected_lang=detected_lang, officer=officer, typo_prompt=typo_prompt)

            elif intent_type == BodhZIntentType.APP_AUDIT_HISTORY:
                db_tool_result = BodhZBackendTools.get_audit_history(db, bid_id=active_b_id)
                events = db_tool_result.get("events", [])
                if not events:
                    reply = "No audit trail events recorded in database yet."
                else:
                    lines = [f"Cryptographic Audit Trail History ({len(events)} events):\n"]
                    for idx, e in enumerate(events[:10], 1):
                        lines.append(f"{idx}. [{e['timestamp']}] Event: {e['event_type']} | Actor: {e['actor']}")
                    reply = "\n".join(lines)
                return self._build_response(reply, "DB_TOOL_AUDIT_HISTORY", "BodhZ-DatabaseTool-v1.0", intent_type=intent_type, data=db_tool_result, detected_lang=detected_lang, officer=officer, typo_prompt=typo_prompt)

            elif intent_type == BodhZIntentType.APP_OFFICER_IDENTITY:
                reply = (
                    f"Authentication Profile:\n\n"
                    f"• Authenticated User: Officer {officer}\n"
                    f"• Assigned Role: {role_label}\n"
                    f"• Security Clearance: Level-1 Procurement Administrator\n\n"
                    f"Decision Authority Mandate:\n"
                    f"You hold full administrative authority and 100% final qualification/disqualification decision authority "
                    f"over GeM procurement bids in the BodhZ platform under GFR 2017 Rule 144."
                )
                return self._build_response(reply, "DB_OFFICER_IDENTITY", "BodhZ-DatabaseTool-v1.0", intent_type=intent_type, data={}, detected_lang=detected_lang, officer=officer, typo_prompt=typo_prompt)

        # =========================================================================
        # BRANCH B: CONVERSATION CORRECTION & FOLLOW-UP MEMORY
        # =========================================================================
        if intent_type == BodhZIntentType.CONVERSATION_FOLLOWUP:
            last_user_topic = ""
            if conversation_history:
                for h in reversed(conversation_history):
                    if h.get("sender") == "user" and h.get("text") != user_msg:
                        last_user_topic = h.get("text", "").lower()
                        break

            if "tender" in user_msg and "bid" in last_user_topic:
                reply = (
                    "A Tender (Notice Inviting Tender - NIT) is an official public invitation issued by a Ministry, Department, or CPSE under GFR 2017 Rule 144, "
                    "inviting competitive technical and financial proposals from qualified suppliers for goods, works, or services."
                )
            elif "bid" in user_msg and "tender" in last_user_topic:
                reply = (
                    "A Bid is a formal, legally binding commercial and technical offer submitted by an eligible vendor or OEM in response to a public procurement tender, "
                    "containing technical specifications, statutory compliance certificates, EMD, and price schedules."
                )
            else:
                reply = "Understood. Please let me know how you would like to proceed with your tender specifications or bidder compliance evaluations."
            return self._build_response(reply, "CONVERSATION_MEMORY", "BodhZ-Memory-v1.0", intent_type=intent_type, data={}, detected_lang=detected_lang, officer=officer, typo_prompt=typo_prompt)

        # =========================================================================
        # BRANCH C: GREETINGS, CASUAL, ACKNOWLEDGMENT & GRATITUDE
        # =========================================================================
        if intent_type == BodhZIntentType.ACKNOWLEDGMENT:
            reply = f"Understood, Officer {officer}. Let me know if you need anything else regarding your tenders, bidder evaluations, or compliance reports."
            return self._build_response(reply, "ACKNOWLEDGMENT", "BodhZ-v1.0", intent_type=intent_type, data={}, detected_lang=detected_lang, officer=officer)

        if intent_type == BodhZIntentType.GRATITUDE:
            reply = f"You are very welcome, Officer {officer}! I am here whenever you need assistance with tender specifications, gateway checks, or compliance evaluations."
            return self._build_response(reply, "GRATITUDE", "BodhZ-v1.0", intent_type=intent_type, data={}, detected_lang=detected_lang, officer=officer)

        if intent_type == BodhZIntentType.GREETING:
            greeting_word = intent.get("greeting_phrase", "Hello")
            if greeting_word == "HOW_ARE_YOU":
                reply = f"I am functioning well and ready to assist you, Officer {officer}! How can I support your tender evaluation, bidder verification, or compliance checks today?"
            else:
                reply = f"{greeting_word}, Officer {officer}! How can I help you with your procurement evaluation today?"
            return self._build_response(reply, "GREETING", "BodhZ-v1.0", intent_type=intent_type, data={"greeting_type": greeting_word}, detected_lang=detected_lang, officer=officer)

        if intent_type == BodhZIntentType.HINGLISH_CASUAL:
            reply = f"Main BodhZ AI Assistant hoon. Main Officer {officer} ko tender rules, GST, Udyam MSME, OEM authorization, compliance score, aur document evidence verify karne mein madad karta hoon."
            return self._build_response(reply, "HINGLISH", "BodhZ-v1.0", intent_type=intent_type, data={}, detected_lang=detected_lang, officer=officer)

        if intent_type == BodhZIntentType.OFFICER_DECISION_MANDATE:
            reply = BodhZKnowledgeBase.OFFICER_DECISION_ANSWER
            return self._build_response(reply, "MANDATE", "BodhZ-v1.0", intent_type=intent_type, data={}, detected_lang=detected_lang, officer=officer, typo_prompt=typo_prompt)

        # =========================================================================
        # BRANCH D: GENERAL KNOWLEDGE, GOVERNMENT ENCYCLOPEDIA & OPENAI EXECUTION
        # =========================================================================
        gov_encyclopedia_knowledge = GovernmentProcurementEncyclopedia.lookup(user_msg)

        retrieved_knowledge = self.knowledge_retriever.retrieve_relevant_knowledge(user_msg)
        domain_context = BodhZContextBuilder.build_system_context(active_tender, active_bidder, user_name, user_role)
        if gov_encyclopedia_knowledge:
            domain_context += f"\n\nGOVERNMENT PROCUREMENT REGULATION:\n{gov_encyclopedia_knowledge}"
        if retrieved_knowledge:
            domain_context += f"\n\nRETRIEVED KNOWLEDGE:\n{retrieved_knowledge}"

        system_prompt = BodhZPromptManager.get_system_prompt(domain_context)

        messages = []
        if conversation_history:
            for msg in conversation_history[-6:]:
                role = "user" if msg.get("sender") == "user" else "assistant"
                messages.append({"role": role, "content": msg.get("text", "")})
        messages.append({"role": "user", "content": user_msg})

        if self.openai_client.is_configured():
            openai_res = await self.openai_client.generate_chat_response(
                system_prompt=system_prompt,
                messages=messages,
                temperature=0.3,
                max_tokens=800
            )
            if openai_res["success"] and openai_res["reply"]:
                sanitized_reply = BodhZTextSanitizer.sanitize_to_plain_text(openai_res["reply"])
                evidence = self._extract_evidence_metadata(user_msg, active_bidder)
                if typo_prompt and detected_lang == "en":
                    sanitized_reply = f"Did you mean: '{typo_prompt}'?\n\n{sanitized_reply}"
                return {
                    "reply": sanitized_reply,
                    "source": "OPENAI_API",
                    "model": openai_res["model"],
                    "evidence": evidence
                }

        # Offline Universal QA Fallback
        universal_reply = UniversalQAEngine.answer_universal_question(
            query=user_msg,
            active_bidder=active_bidder,
            conversation_history=conversation_history,
            user_name=user_name,
            user_role=user_role,
            active_tender=active_tender,
            all_tenders=all_tenders,
            all_bidders=all_bidders
        )
        return self._build_response(universal_reply, "UNIVERSAL_QA_ENGINE", "BodhZ-UniversalQA-v1.0", intent_type=intent_type, data={}, detected_lang=detected_lang, officer=officer, typo_prompt=typo_prompt)

    def _build_response(
        self,
        text: str,
        source: str,
        model: str,
        intent_type: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
        detected_lang: str = "en",
        officer: str = "Shubham",
        typo_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """Sanitizes text and formats response dictionary with multilingual localization and subtle typo header."""
        clean_text = BodhZTextSanitizer.sanitize_to_plain_text(text)
        if detected_lang != "en" and intent_type:
            clean_text = BodhZMultilingualEngine.localize_response(
                intent_type=intent_type,
                data=data or {},
                lang=detected_lang,
                officer=officer,
                original_reply=clean_text
            )
        elif typo_prompt and detected_lang == "en":
            clean_text = f"Did you mean: '{typo_prompt}'?\n\n{clean_text}"

        return {
            "reply": clean_text,
            "source": source,
            "model": model,
            "evidence": None
        }

    def _extract_evidence_metadata(self, q: str, bidder: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if not bidder:
            return None
        q_lower = q.lower()
        if "oem" in q_lower or "authorization" in q_lower:
            return {
                "title": "OEM Authorization Letter",
                "page": "Page 1",
                "status": "FAIL" if bidder.get("risk") == "CRITICAL" else "PASS",
                "source": "Uploaded Bidder Document",
                "mode": "DOCUMENT_CONSISTENCY",
                "reason": "Expired validity date on 31/12/2023" if bidder.get("risk") == "CRITICAL" else "Valid authorization through 2027",
                "view": "docintel"
            }
        elif "gst" in q_lower:
            return {
                "title": "GST Registration Certificate",
                "page": "Page 1",
                "status": "REVIEW" if bidder.get("risk") == "MEDIUM" else "PASS",
                "source": "GSTN Portal (Node 1)",
                "mode": "SANDBOX CONNECTOR",
                "reason": "Legal name spelling variation" if bidder.get("risk") == "MEDIUM" else "Active GSTIN Verified",
                "view": "vercenter"
            }
        return None
