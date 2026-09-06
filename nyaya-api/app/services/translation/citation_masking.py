import re
from typing import Tuple, Dict, List, Set


# Patterns for Indian legal citations, paragraph brackets, statutes, and case names
CITATION_REGEX = re.compile(r"\(\d{4}\)\s+\d+\s+SCC\s+\d+(?:,\s*para\s+\d+)?|\d{4}\s+INSC\s+\d+|\(\d{4}\)\s+\d+\s+SCR\s+\d+", re.IGNORECASE)
PARAGRAPH_REGEX = re.compile(r"\[Paras?\s+[\d,\s\-and]+\]|Paragraphs?\s+[\d,\s\-and]+|Para\s+\d+", re.IGNORECASE)
STATUTE_REGEX = re.compile(
    r"Section\s+\d+[A-Za-z]?(?:\(\d+\))?(?:\([a-z]\))?|Order\s+[IVXLCDM]+\s+Rule\s+\d+(?:\(\d+\))?|"
    r"Commercial Courts Act,\s*2015|Arbitration and Conciliation Act,\s*1996|Indian Contract Act,\s*1872|"
    r"Code of Civil Procedure,\s*1908|CPC",
    re.IGNORECASE
)
CASE_NAME_REGEX = re.compile(
    r"Patil Automation Private Limited and Others v\. Rakheja Engineers Private Limited|"
    r"Patil Automation Private Limited|Patil Automation|"
    r"In Re:? Interplay Between Arbitration Agreements[^,\.\n]+|"
    r"SMS Tea Estates Pvt\. Ltd\. v\. Chandmari Tea Co\. Pvt\. Ltd\.|SMS Tea Estates|"
    r"Vidya Drolia and Others v\. Durga Trading Corporation|Vidya Drolia|"
    r"ONGC Ltd\. v\. Saw Pipes Ltd\.|ONGC v\. Saw Pipes|"
    r"Kailash Nath Associates v\. Delhi Development Authority|Kailash Nath Associates|"
    r"Ambalal Sarabhai Enterprises Ltd\.|Sudhir Kumar @ S\. Baliyan",
    re.IGNORECASE
)


class CitationMaskingService:
    """
    Two-pass citation and legal entity masking service.
    Replaces citations, statutory sections, paragraph numbers, and case names with
    immutable anchor tokens before translation, and cleanly restores them post-translation.
    """

    @staticmethod
    def mask_legal_entities(text: str) -> Tuple[str, Dict[str, str]]:
        """
        Masks citations, paragraph numbers, statutory provisions, and case names.
        Returns the masked text and a mapping from token back to original string.
        """
        token_map: Dict[str, str] = {}
        counter = 0

        # 1. Mask exact citations
        def replace_cite(match):
            nonlocal counter
            token = f"NYAYA_CITE_{counter}"
            counter += 1
            token_map[token] = match.group(0)
            return token

        masked = CITATION_REGEX.sub(replace_cite, text)

        # 2. Mask paragraph pinpoints
        def replace_para(match):
            nonlocal counter
            token = f"NYAYA_PARA_{counter}"
            counter += 1
            token_map[token] = match.group(0)
            return token

        masked = PARAGRAPH_REGEX.sub(replace_para, masked)

        # 3. Mask case names
        def replace_case(match):
            nonlocal counter
            token = f"NYAYA_CASE_{counter}"
            counter += 1
            token_map[token] = match.group(0)
            return token

        masked = CASE_NAME_REGEX.sub(replace_case, masked)

        # 4. Mask statutes and sections
        def replace_statute(match):
            nonlocal counter
            token = f"NYAYA_STAT_{counter}"
            counter += 1
            token_map[token] = match.group(0)
            return token

        masked = STATUTE_REGEX.sub(replace_statute, masked)

        return masked, token_map

    @staticmethod
    def unmask_legal_entities(masked_text: str, token_map: Dict[str, str]) -> str:
        """Restores masked tokens back to their original authoritative strings."""
        result = masked_text
        for token, original in token_map.items():
            pattern = re.compile(re.escape(token), re.IGNORECASE)
            result = pattern.sub(original, result)
        return result

    @staticmethod
    def verify_citation_integrity(
        original_text: str,
        translated_text: str,
        required_citations: Set[str] = None
    ) -> Tuple[bool, List[str]]:
        """
        Verifies that all citations and paragraph pinpoints present in the original text
        are preserved intact in the translated text.
        Returns (is_valid, list_of_violations).
        """
        violations = []

        # Find all citations in original
        orig_citations = set(CITATION_REGEX.findall(original_text))
        if required_citations:
            orig_citations.update(required_citations)

        for cite in orig_citations:
            if cite not in translated_text:
                violations.append(f"Missing or modified citation: '{cite}'")

        # Find all paragraph pinpoints in original
        orig_paras = set(PARAGRAPH_REGEX.findall(original_text))
        for para in orig_paras:
            # Check if paragraph number itself is preserved
            numbers = re.findall(r"\d+", para)
            for num in numbers:
                if num not in translated_text:
                    violations.append(f"Missing or modified paragraph pinpoint: '{num}'")

        return len(violations) == 0, violations
