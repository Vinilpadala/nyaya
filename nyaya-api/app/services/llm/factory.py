import logging
from app.core.config import settings
from app.services.llm.base import BaseLLMProvider
from app.services.llm.gemini_provider import GeminiProvider

logger = logging.getLogger(__name__)

def get_llm_provider() -> BaseLLMProvider:
    """
    Factory function returning the configured LLM provider.
    Nyaya AI components interact exclusively through BaseLLMProvider interface.
    """
    provider_type = settings.LLM_PROVIDER.lower().strip()
    if provider_type == "gemini":
        return GeminiProvider()
    
    # Fallback to GeminiProvider default
    logger.info(f"Unrecognized LLM provider '{provider_type}', falling back to GeminiProvider.")
    return GeminiProvider()
