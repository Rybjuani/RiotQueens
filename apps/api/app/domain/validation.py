import re

from .contracts import OutputValidationResult

CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")
INTERNAL_LEAKS = ("<|system|>", "system prompt", "tool_calls", "you are an ai")


class OutputValidator:
    """Small deterministic gate; it is not a semantic moderation system."""

    def validate(self, content: str) -> OutputValidationResult:
        reasons: list[str] = []
        stripped = content.strip()
        sanitized = CONTROL_CHARS.sub("", content).strip()
        encoding_ok = not CONTROL_CHARS.search(content)
        language_ok = self._looks_like_spanish(stripped)
        not_truncated = not content.rstrip().endswith(("...", "…", ":"))
        not_repetitive = self._not_repetitive(stripped)
        no_internal_leak = not any(marker in stripped.lower() for marker in INTERNAL_LEAKS)
        character_consistent = not self._looks_like_internal_fragment(stripped)
        if not sanitized:
            reasons.append("empty_response")
        if len(stripped) > 12_000:
            reasons.append("excessive_length")
        if not encoding_ok:
            reasons.append("control_character")
        if not language_ok:
            reasons.append("unexpected_language")
        if not not_truncated:
            reasons.append("possible_truncation")
        if not not_repetitive:
            reasons.append("excessive_repetition")
        if not no_internal_leak:
            reasons.append("internal_fragment")
        if not character_consistent:
            reasons.append("unusual_internal_format")
        return OutputValidationResult(
            is_valid=not reasons,
            language_ok=language_ok,
            encoding_ok=encoding_ok,
            not_truncated=not_truncated,
            not_repetitive=not_repetitive,
            no_internal_leak=no_internal_leak,
            character_consistent=character_consistent,
            reasons=reasons,
        )

    @staticmethod
    def _looks_like_spanish(text: str) -> bool:
        if not text:
            return False
        if re.search(r"[\u0400-\u04ff\u3040-\u30ff\u4e00-\u9fff]", text):
            return False
        words = set(re.findall(r"[a-záéíóúñü]+", text.lower()))
        markers = {"que", "de", "la", "el", "te", "me", "una", "con", "para", "hola"}
        latin = len(re.findall(r"[A-Za-zÁÉÍÓÚáéíóúÑñÜü]", text))
        return latin > 0 and (bool(words & markers) or len(text.split()) < 4)

    @staticmethod
    def _not_repetitive(text: str) -> bool:
        words = text.lower().split()
        if len(words) < 8:
            return True
        if len(set(words)) / len(words) < 0.35:
            return False
        symbols = sum(not char.isalnum() and not char.isspace() for char in text)
        return symbols / max(len(text), 1) < 0.35

    @staticmethod
    def _looks_like_internal_fragment(text: str) -> bool:
        return text.startswith(("```", '{"', "[SYSTEM", "<assistant>"))
