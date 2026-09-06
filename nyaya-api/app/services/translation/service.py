import logging
from typing import Tuple, Optional, Dict, Any
from app.services.translation.gemini_translator import GeminiTranslationProvider
from app.services.translation.deterministic_translator import DeterministicLegalTranslator
from app.services.translation.bhashini_adapter import BhashiniTranslationProvider

logger = logging.getLogger(__name__)

# Institutional disclaimer notice displayed whenever translation is active
TRANSLATION_ACTIVE_DISCLAIMER = (
    "Judicial Translation Notice: AI-assisted chambers translation for reference only. "
    "Primary law reports (SCC/SCR), legal citations, and statutory enactments remain authoritative in English."
)

TRANSLATION_FALLBACK_DISCLAIMER = (
    "Judicial Translation Notice: Vernacular translation service is temporarily unavailable. "
    "Nyaya AI has returned the authoritative English grounded synthesis to preserve legal citation integrity."
)


class TranslationService:
    """
    Unified judicial translation service orchestrating query conversion (ingress)
    and synthesis translation (egress) with fallback to English.
    """

    def __init__(self):
        self.gemini_provider = GeminiTranslationProvider()
        self.deterministic_provider = DeterministicLegalTranslator()
        self.bhashini_provider = BhashiniTranslationProvider()

    def translate_query_to_english(self, query: str, language: str) -> Tuple[str, str]:
        """
        Translates query to English for legal BM25 retrieval.
        Returns (english_query, translation_engine_used).
        """
        lang = (language or "en").lower().strip()
        if lang == "en" or not query.strip():
            return query, "Source English"

        # 1. Try Bhashini if configured (sovereign priority)
        if self.bhashini_provider.is_available():
            res = self.bhashini_provider.translate_query_to_english(query, lang)
            if res:
                return res, self.bhashini_provider.get_provider_name()

        # 2. Try Gemini translation
        if self.gemini_provider.is_available():
            res = self.gemini_provider.translate_query_to_english(query, lang)
            if res:
                return res, self.gemini_provider.get_provider_name()

        # 3. Try deterministic keyword mapping
        res = self.deterministic_provider.translate_query_to_english(query, lang)
        if res:
            return res, self.deterministic_provider.get_provider_name()

        # 4. Fallback: return original query (or extracted alphanumeric tokens)
        logger.info(f"Query translation yielded no terms for '{query}'. Using original query as fallback.")
        return query, "Original Query Pass-through"

    def translate_synthesis(
        self,
        summary: str,
        analysis: str,
        target_language: str
    ) -> Dict[str, Any]:
        """
        Translates grounded judicial synthesis into target_language.
        Returns dict with keys:
            translated_summary, translated_analysis, translation_engine, translation_notice
        """
        lang = (target_language or "en").lower().strip()
        if lang == "en":
            return {
                "translated_summary": None,
                "translated_analysis": None,
                "translation_engine": "Source English",
                "translation_notice": None,
            }

        # 1. Try Bhashini if active
        if self.bhashini_provider.is_available():
            trans_sum = self.bhashini_provider.translate_legal_text(summary, lang)
            if trans_sum:
                return {
                    "translated_summary": trans_sum,
                    "translated_analysis": None,
                    "translation_engine": self.bhashini_provider.get_provider_name(),
                    "translation_notice": TRANSLATION_ACTIVE_DISCLAIMER,
                }

        # 2. Try Gemini translation
        if self.gemini_provider.is_available():
            trans_sum = self.gemini_provider.translate_legal_text(summary, lang)
            if trans_sum:
                return {
                    "translated_summary": trans_sum,
                    "translated_analysis": None,
                    "translation_engine": self.gemini_provider.get_provider_name(),
                    "translation_notice": TRANSLATION_ACTIVE_DISCLAIMER,
                }

        # 3. Try Deterministic Legal Translator (pre-compiled benchmark templates)
        trans_sum = self.deterministic_provider.translate_legal_text(summary, lang)
        if trans_sum:
            return {
                "translated_summary": trans_sum,
                "translated_analysis": None,
                "translation_engine": self.deterministic_provider.get_provider_name(),
                "translation_notice": TRANSLATION_ACTIVE_DISCLAIMER,
            }

        # 4. Fallback: In strict accordance with Phase 7 Guardrail 5, if complete safe translation
        # is unavailable, fall back to English with a clear disclaimer rather than corrupting legal text.
        logger.warning(
            f"Translation into '{target_language}' unavailable. Falling back to English research briefing."
        )
        return {
            "translated_summary": None,
            "translated_analysis": None,
            "translation_engine": "Fallback to Authoritative English",
            "translation_notice": TRANSLATION_FALLBACK_DISCLAIMER,
        }
