import os
import logging
import httpx
from typing import List, Dict, Any
from dotenv import load_dotenv
from app.core.config import settings

logger = logging.getLogger(__name__)

# --------------------------------------------------
# OPENAI BACKEND CLIENT WRAPPER (SIH26100 RESPONSES API)
# --------------------------------------------------
class OpenAIBackendClient:
    """
    Secure backend-only client for calling OpenAI Responses API & ChatCompletions API.
    
    Security & Architecture Rules:
    - Never exposes API keys to client/frontend.
    - Dynamically reloads .env if key is updated.
    - Configurable model via settings.OPENAI_MODEL.
    - Handles timeouts, rate limits, and API failures gracefully.
    - Returns structured text response.
    """

    def __init__(self):
        self.responses_url = "https://api.openai.com/v1/responses"
        self.chat_url = "https://api.openai.com/v1/chat/completions"

    def get_api_key(self) -> str:
        """Dynamically retrieves active API key from environment or .env file."""
        # Check current env
        key = os.getenv("OPENAI_API_KEY") or settings.OPENAI_API_KEY or ""
        if not key or key.startswith("your_"):
            # Try reloading from .env file
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            env_path = os.path.join(base_dir, ".env")
            if os.path.exists(env_path):
                load_dotenv(env_path, override=True)
                key = os.getenv("OPENAI_API_KEY", "")
        return key.strip()

    def get_model(self) -> str:
        """Retrieves configured OpenAI model name."""
        return os.getenv("OPENAI_MODEL", settings.OPENAI_MODEL or "gpt-5.4-mini")

    def is_configured(self) -> bool:
        """Checks if a valid OpenAI API key is configured."""
        key = self.get_api_key()
        return bool(key and len(key) > 10 and not key.startswith("your_"))

    def _extract_text_from_responses_api(self, data: Dict[str, Any]) -> str:
        """Parses output text from OpenAI Responses API payload structure."""
        if "output" in data:
            out = data["output"]
            if isinstance(out, str):
                return out
            if isinstance(out, list):
                text_parts = []
                for item in out:
                    if isinstance(item, dict):
                        contents = item.get("content", [])
                        if isinstance(contents, list):
                            for c in contents:
                                if isinstance(c, dict) and "text" in c:
                                    text_parts.append(c["text"])
                                elif isinstance(c, str):
                                    text_parts.append(c)
                        elif isinstance(contents, str):
                            text_parts.append(contents)
                if text_parts:
                    return "\n".join(text_parts)

        if "choices" in data and len(data["choices"]) > 0:
            msg = data["choices"][0].get("message", {})
            if isinstance(msg, dict) and "content" in msg:
                return msg["content"]
            elif "text" in data["choices"][0]:
                return data["choices"][0]["text"]

        return ""

    async def generate_chat_response(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.4,
        max_tokens: int = 700
    ) -> Dict[str, Any]:
        """
        Sends messages to OpenAI API (trying Responses API endpoint first, with ChatCompletions fallback).
        """
        api_key = self.get_api_key()
        model_name = self.get_model()

        if not api_key or len(api_key) <= 10 or api_key.startswith("your_"):
            logger.info("OpenAI API Key not configured. Using BodhZ Grounded Local Knowledge Engine.")
            return {"success": False, "reply": None, "source": "LOCAL_ENGINE", "reason": "API_KEY_NOT_SET"}

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        # 1. TRY OPENAI RESPONSES API ENDPOINT (https://api.openai.com/v1/responses)
        last_user_msg = messages[-1]["content"] if messages else ""
        combined_input = f"System Instructions: {system_prompt}\n\nUser Question: {last_user_msg}"

        responses_payload = {
            "model": model_name,
            "input": combined_input,
            "store": True
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(self.responses_url, headers=headers, json=responses_payload)
                if resp.status_code == 200:
                    data = resp.json()
                    extracted_text = self._extract_text_from_responses_api(data)
                    
                    if extracted_text:
                        return {
                            "success": True,
                            "reply": extracted_text,
                            "model": data.get("model", model_name),
                            "source": "OPENAI_RESPONSES_API"
                        }
                else:
                    logger.warning(f"Responses API returned HTTP {resp.status_code}: {resp.text}")
        except Exception as e:
            logger.warning(f"Responses API endpoint call failed, attempting ChatCompletions fallback: {e}")

        # 2. CHATCOMPLETIONS FALLBACK (https://api.openai.com/v1/chat/completions)
        fallback_model = model_name if model_name != "gpt-5.4-mini" else "gpt-4o-mini"
        full_messages = [{"role": "system", "content": system_prompt}] + messages
        chat_payload = {
            "model": fallback_model,
            "messages": full_messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(self.chat_url, headers=headers, json=chat_payload)
                if resp.status_code == 200:
                    data = resp.json()
                    content = data["choices"][0]["message"]["content"]
                    return {
                        "success": True,
                        "reply": content,
                        "model": data.get("model", fallback_model),
                        "source": "OPENAI_CHAT_API"
                    }
                else:
                    logger.error(f"OpenAI Chat API returned HTTP {resp.status_code}: {resp.text}")
                    return {"success": False, "reply": None, "source": "LOCAL_ENGINE", "reason": f"HTTP_{resp.status_code}"}
        except Exception as e:
            logger.error(f"Failed to connect to OpenAI API: {str(e)}")
            return {"success": False, "reply": None, "source": "LOCAL_ENGINE", "reason": str(e)}
