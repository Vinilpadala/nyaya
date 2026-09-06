from abc import ABC, abstractmethod
from typing import Optional
from app.services.llm.evidence_pack import EvidencePack
from app.services.llm.schemas import GroundedSynthesisStructuredOutput

class BaseLLMProvider(ABC):
    """
    Abstract Base Class for LLM providers in Nyaya AI.
    Decouples the RAG Orchestrator from specific model providers (Gemini, local LLMs, etc.).
    """

    @abstractmethod
    def is_available(self) -> bool:
        """Returns True if the provider is configured and available for inference."""
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """Returns the canonical name and model identifier of the provider."""
        pass

    @abstractmethod
    def generate_grounded_synthesis(
        self,
        evidence_pack: EvidencePack
    ) -> Optional[GroundedSynthesisStructuredOutput]:
        """
        Executes grounded synthesis using the provided Evidence Pack.
        Returns a structured output or None if generation failed/is unavailable.
        """
        pass
