import json
import re
import logging
from typing import Optional
from app.core.config import settings
from app.services.llm.base import BaseLLMProvider
from app.services.llm.evidence_pack import EvidencePack
from app.services.llm.schemas import GroundedSynthesisStructuredOutput

logger = logging.getLogger(__name__)

SYSTEM_INSTRUCTION = """You are Nyaya AI, a legal research synthesis assistant for authorized judicial research.

Your task is to synthesize ONLY the legal material contained in the supplied evidence.

You must not invent, infer, or fabricate:
- cases
- statutes
- citations
- paragraph numbers
- quotations
- facts
- procedural history
- holdings
- legal propositions

Every authority mentioned in your response must correspond to an authority in the supplied evidence.

Every pinpoint paragraph must correspond to a supplied passage.

Every quotation must be supported by the supplied source passage.

If the supplied evidence is insufficient to answer the research issue, explicitly state that the available curated corpus does not contain sufficient supporting authority.

Do not treat absence of treatment data as proof that an authority is universally good law.

Do not overstate the authority of High Court decisions.

Preserve distinctions, modifications, conflicts, and overruled status supplied by the evidence.

You are an assistive research system, not the judicial decision-maker.

Do not predict or determine the outcome of a case in this phase.
"""

class GeminiProvider(BaseLLMProvider):
    """
    Google Gemini implementation of BaseLLMProvider using the modern google-genai SDK.
    Follows conservative synthesis configuration, strict evidence grounding,
    and server-side secret isolation.
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
                # Never print the API key or raw headers in logs
                logger.warning(f"Failed to initialize Google GenAI client: {type(e).__name__}")
                self._client = None

    def is_available(self) -> bool:
        """Returns True if a valid-appearing Gemini API key is configured."""
        return bool(self.api_key and self.api_key.strip() and len(self.api_key.strip()) > 10)

    def get_provider_name(self) -> str:
        return f"Google Gemini ({self.model})"

    def _format_prompt(self, evidence_pack: EvidencePack) -> str:
        """Constructs a clean, structured prompt strictly separating source material from analysis."""
        evidence_dict = {
            "query": evidence_pack.query,
            "commercial_domain": evidence_pack.commercial_domain,
            "authorities": [
                {
                    "case_id": a.case_id,
                    "title": a.title,
                    "citation": a.citation,
                    "court": a.court,
                    "year": a.year,
                    "bench_strength": a.bench_strength,
                    "judgment_date": a.decision_date,
                    "treatment_status": a.treatment_status,
                    "negative_treatment_found": a.negative_treatment_found,
                    "treatment_summary": a.treatment_summary,
                    "key_ratio": a.key_ratio,
                    "available_paragraphs": a.available_paragraphs,
                    "passages": [
                        {
                            "paragraph_number": p.paragraph_number,
                            "text": p.text,
                            "topic": p.legal_topic,
                        }
                        for p in a.passages
                    ],
                }
                for a in evidence_pack.authorities
            ],
            "governing_statutes": [
                {
                    "act": s.act_title,
                    "section": s.section_number,
                    "title": s.section_title,
                    "text": s.text,
                    "relevance": s.commercial_relevance,
                }
                for s in evidence_pack.statutes
            ],
            "corpus_limitation_notice": evidence_pack.corpus_boundary_note,
        }

        return (
            "====================================================================\n"
            "SOURCE MATERIAL (VERIFIED EVIDENCE PACK — SOURCE OF TRUTH)\n"
            "====================================================================\n"
            f"{json.dumps(evidence_dict, indent=2)}\n\n"
            "====================================================================\n"
            "RESEARCH QUERY & TASK INSTRUCTIONS\n"
            "====================================================================\n"
            f"Research Issue: {evidence_pack.query}\n\n"
            "MANDATORY INSTRUCTIONS:\n"
            "1. You must synthesize ONLY the legal material contained in the SOURCE MATERIAL above.\n"
            "2. The model must NOT treat generated analysis as source material. Only the verified precedents,\n"
            "   reported passages, and statutory sections contained in the evidence pack constitute source material.\n"
            "3. If the supplied evidence is insufficient to answer the research issue, explicitly state:\n"
            "   'The available curated corpus does not contain sufficient supporting authority.'\n"
            "4. Preserve distinctions, modifications, conflicts, and overruled status supplied by the evidence.\n"
            "5. Return strictly valid JSON conforming to the requested schema.\n"
        )

    def generate_grounded_synthesis(
        self,
        evidence_pack: EvidencePack
    ) -> Optional[GroundedSynthesisStructuredOutput]:
        """
        Calls the Gemini API with structured output schema and returns GroundedSynthesisStructuredOutput.
        Catches any API or parsing error gracefully and logs cleanly without leaking secrets.
        """
        if not self.is_available() or self._client is None:
            logger.info("GeminiProvider is not available or client uninitialized.")
            return None

        prompt = self._format_prompt(evidence_pack)

        try:
            from google.genai import types

            config = types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=GroundedSynthesisStructuredOutput,
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=settings.LLM_TEMPERATURE,
            )

            response = self._client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=config,
            )

            if not response or not response.text:
                logger.warning("Gemini returned an empty response.")
                return None

            raw_text = response.text.strip()
            # Clean markdown fences if model wraps JSON
            if raw_text.startswith("```"):
                raw_text = re.sub(r"^```(?:json)?\s*", "", raw_text)
                raw_text = re.sub(r"\s*```$", "", raw_text).strip()

            data = json.loads(raw_text)
            structured_output = GroundedSynthesisStructuredOutput.model_validate(data)
            return structured_output

        except Exception as e:
            # Clean sanitization: do not log credentials, tokens, or raw request headers
            error_type = type(e).__name__
            logger.warning(
                f"Gemini grounded synthesis call failed ({error_type}). "
                "Gracefully falling back to deterministic synthesizer."
            )
            return None
