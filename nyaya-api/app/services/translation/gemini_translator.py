import logging
from typing import Optional
from app.core.config import settings
from app.services.translation.base import BaseTranslationProvider
from app.services.translation.citation_masking import CitationMaskingService

logger = logging.getLogger(__name__)

QUERY_TRANSLATION_SYSTEM_PROMPT = """You are Nyaya AI's Judicial Query Translator for Indian Commercial Courts.
Your task is to convert a commercial-law query submitted in an Indian language (e.g., Hindi, Telugu, Tamil, Marathi)
into clean, precise English legal search terms suitable for lexical BM25 and statute retrieval.

Preserve all statutory sections (e.g., Section 12A, Order VII Rule 11 CPC, Section 11, Section 74, Section 34).
Preserve legal doctrine keywords (e.g., pre-institution mediation, rejection of plaint, urgent interim relief, stamping, liquidated damages, arbitrability).
Do not summarize or invent facts. Return ONLY the English search terms string without conversational preamble."""

SYNTHESIS_TRANSLATION_SYSTEM_PROMPT = """You are Nyaya AI's Judicial Translation Engine for Indian Commercial Courts.
Your task is to translate an objective, grounded judicial synthesis briefing into {target_language}.

CRITICAL LEGAL INVARIANTS:
1. IMMUTABLE TOKENS: You will see tokens like NYAYA_CITE_0, NYAYA_PARA_1, NYAYA_CASE_2, NYAYA_STAT_3.
   You MUST PRESERVE THESE EXACT TOKENS CHARACTER-FOR-CHARACTER. Do NOT translate, transliterate, remove, or modify them.
2. CITATIONS AND BRACKETS: Preserve all parenthetical citations, year numbers, and bracketed paragraph numbers.
3. FORMAL JUDICIAL REGISTER: Use a formal, objective, declaring tone appropriate for a High Court Commercial Division Bench memo.
4. ZERO FABRICATION: Do not add any new case names, holdings, statutes, or personal legal opinions.

Translate the provided briefing text faithfully into {target_language}:"""


class GeminiTranslationProvider(BaseTranslationProvider):
    """
    Google Gemini implementation of judicial translation using the google-genai SDK.
    Employs token masking to preserve citation integrity.
    """

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = model or settings.GEMINI_MODEL
        self._client = None
        if self.is_available():
            try:
                from google import genai
                from google.genai import types
                http_options = types.HttpOptions(
                    timeout=int(settings.LLM_TIMEOUT_SECONDS * 1000)
                )
                self._client = genai.Client(api_key=self.api_key, http_options=http_options)
            except Exception as e:
                logger.warning(f"Failed to initialize Google GenAI translation client: {type(e).__name__}")
                self._client = None

    def is_available(self) -> bool:
        return bool(self.api_key and self.api_key.strip() and len(self.api_key.strip()) > 10)

    def get_provider_name(self) -> str:
        return f"Google Gemini Translator ({self.model})"

    def translate_query_to_english(self, query: str, source_language: str) -> Optional[str]:
        """Translates native Indian language query into English legal retrieval keywords."""
        if not self.is_available() or not self._client:
            return None

        try:
            from google.genai import types
            prompt = f"Source Language: {source_language}\nOriginal Judicial Query: {query}\nTranslate to English legal search query:"
            response = self._client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=QUERY_TRANSLATION_SYSTEM_PROMPT,
                    temperature=0.0,
                    max_output_tokens=256,
                ),
            )
            if response and response.text:
                return response.text.strip().strip('"')
            return None
        except Exception as e:
            logger.warning(f"Query translation failed ({type(e).__name__}): {e}")
            return None

    def translate_legal_text(self, text: str, target_language: str) -> Optional[str]:
        """
        Translates legal briefing text into target_language with two-pass citation masking.
        Returns translated text or None on failure/violation.
        """
        if not self.is_available() or not self._client or not text.strip():
            return None

        # 1. Mask legal entities
        masked_text, token_map = CitationMaskingService.mask_legal_entities(text)

        language_names = {
            "hi": "Hindi (हिन्दी)",
            "te": "Telugu (తెలుగు)",
            "ta": "Tamil (தமிழ்)",
            "mr": "Marathi (मराठी)",
        }
        lang_label = language_names.get(target_language.lower(), target_language)

        try:
            from google.genai import types
            prompt = f"Text to translate into {lang_label}:\n\n{masked_text}"
            response = self._client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYNTHESIS_TRANSLATION_SYSTEM_PROMPT.format(target_language=lang_label),
                    temperature=0.0,
                    max_output_tokens=1500,
                ),
            )
            if not response or not response.text:
                return None

            raw_translation = response.text.strip()

            # 2. Unmask legal entities
            unmasked_translation = CitationMaskingService.unmask_legal_entities(raw_translation, token_map)

            # 3. Verify citation integrity
            is_valid, violations = CitationMaskingService.verify_citation_integrity(text, unmasked_translation)
            if not is_valid:
                logger.warning(f"Translation citation integrity check failed: {violations}. Reverting to English.")
                return None

            return unmasked_translation

        except Exception as e:
            logger.warning(f"Synthesis translation failed ({type(e).__name__}): {e}")
            return None
