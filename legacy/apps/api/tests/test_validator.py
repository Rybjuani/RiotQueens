from app.domain.validation import OutputValidator


def test_accepts_normal_spanish_output() -> None:
    result = OutputValidator().validate("Hola, qué bueno leerte. Podemos seguir con esa idea.")
    assert result.is_valid


def test_rejects_corrupted_multilingual_output() -> None:
    result = OutputValidator().validate("Hola que tal <|system|> Я понимаю 你好 !!! !!! !!!")
    assert not result.is_valid
    assert "internal_fragment" in result.reasons
    assert "unexpected_language" in result.reasons


def test_rejects_empty_and_control_characters() -> None:
    result = OutputValidator().validate("\x00")
    assert not result.is_valid
    assert "empty_response" in result.reasons
    assert "control_character" in result.reasons
