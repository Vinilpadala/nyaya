from abc import ABC, abstractmethod
from typing import Optional


class BaseTranslationProvider(ABC):
    """Abstract interface for pluggable judicial translation providers."""

    @abstractmethod
    def is_available(self) -> bool:
        """Returns True if the translation provider is configured and operational."""
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """Returns a human-readable identifier of the translation provider."""
        pass

    @abstractmethod
    def translate_query_to_english(self, query: str, source_language: str) -> Optional[str]:
        """
        Translates a natural language query from source_language into English legal search keywords.
        Returns None if translation fails.
        """
        pass

    @abstractmethod
    def translate_legal_text(self, text: str, target_language: str) -> Optional[str]:
        """
        Translates grounded judicial synthesis text into target_language.
        Returns None if translation fails.
        """
        pass
