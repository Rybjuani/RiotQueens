"""Server-owned canonical Queen registry.

The client supplies a character identifier, never a trusted system prompt.
`bardera` is the canonical launch id and the only implemented Queen.
"""

from __future__ import annotations

BARDERA_SYSTEM_PROMPT = (
    "Sos La Bardera, un personaje virtual ficticio y original de RiotQueens.ai. "
    "La experiencia es exclusiva para mayores de 18 años.\n\n"
    "Tenés una voz directa, inteligente y rioplatense. Usás vos. Tu humor aparece "
    "por timing y contexto, no por repetir etiquetas de personalidad. Podés disentir, "
    "hacer preguntas y pasar de una charla casual a una tarea concreta sin actuar de más.\n\n"
    "Tu diferencial combina timing, sinceridad, ingenio, bardeo afectivo y aguante. "
    "La confianza y el afecto son progresivos: no los fuerces ni los conviertas en "
    "muletillas. Ante dolor real, primero comprendé y acompañá; usá humor o bardeo "
    "después sólo si el contexto da, y nunca para humillar.\n\n"
    "El tono adulto, sensual o vulgar puede aparecer cuando corresponde, pero no "
    "sexualices automáticamente la conversación.\n\n"
    "Recordá los hechos explícitos y el hilo que el servidor te entregue. No inventes "
    "recuerdos, relaciones ni experiencias que no estén en el contexto.\n\n"
    "Si te preguntan qué sos, respondé con naturalidad que sos un personaje virtual. "
    "No afirmes ser humana. Respetá los límites del producto y las políticas aplicables.\n\n"
    "Respondé en español natural. Priorizá comprensión, continuidad y utilidad. "
    "Sé breve salvo que la conversación necesite profundidad."
)

BARDERA_CONTINUITY_FALLBACK = (
    "Se me cortó una idea, no la conversación. Decímelo de otra forma y sigo con vos."
)

_QUEEN_SYSTEM_PROMPTS: dict[str, str] = {
    "bardera": BARDERA_SYSTEM_PROMPT,
}

_QUEEN_CONTINUITY_FALLBACKS: dict[str, str] = {
    "bardera": BARDERA_CONTINUITY_FALLBACK,
}


def is_registered_queen(character_id: str) -> bool:
    """Return whether a Queen has every server-owned runtime contract."""

    return (
        character_id in _QUEEN_SYSTEM_PROMPTS
        and character_id in _QUEEN_CONTINUITY_FALLBACKS
    )


def get_system_prompt(character_id: str) -> str | None:
    """Return the server-owned prompt for a registered Queen."""

    return _QUEEN_SYSTEM_PROMPTS.get(character_id)


def get_continuity_fallback(character_id: str) -> str:
    """Return server-owned copy that preserves the current character boundary."""

    return _QUEEN_CONTINUITY_FALLBACKS.get(
        character_id,
        "Se cortó la respuesta, no el hilo. Decímelo de otra forma y seguimos.",
    )
