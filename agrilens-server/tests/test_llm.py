"""
tests/test_llm.py
==================
Unit and integration tests for Phase 2 LLM Integration and Chain-of-Thought (CoT) Explainer.
"""
import io
from unittest.mock import MagicMock, patch

import pytest
from httpx import AsyncClient
from PIL import Image

from app.core.llm.cot import ChainOfThoughtExplainer, DiagnosisExplanation
from app.core.llm.engine import LLMEngine


def _create_test_image_bytes(width: int = 224, height: int = 224) -> bytes:
    """Create a synthetic RGB image as PNG bytes for testing."""
    img = Image.new("RGB", (width, height), color=(34, 139, 34))  # Forest green
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def test_cot_explainer_parses_json_response_correctly():
    """ChainOfThoughtExplainer should delegate completion to the engine and parse JSON results."""
    mock_engine = MagicMock(spec=LLMEngine)
    mock_engine.complete_json.return_value = {
        "thinking": "Reasoning about Leaf Blast.",
        "explanation": "Leaf Blast causes diamond-shaped lesions.",
        "recommendation": "Destroy infected crops and avoid excessive nitrogen.",
        "severity": "high",
    }

    explainer = ChainOfThoughtExplainer(mock_engine)
    result = explainer.explain(disease="Leaf Blast", confidence=0.88)

    assert isinstance(result, DiagnosisExplanation)
    assert result.thinking == "Reasoning about Leaf Blast."
    assert result.explanation == "Leaf Blast causes diamond-shaped lesions."
    assert result.recommendation == "Destroy infected crops and avoid excessive nitrogen."
    assert result.severity == "high"
    mock_engine.complete_json.assert_called_once()


@pytest.mark.asyncio
async def test_detect_endpoint_returns_cot_explanation_when_configured(client: AsyncClient):
    """Detection endpoint should invoke LLM explainer and return result when OpenAI API key is present."""
    image_bytes = _create_test_image_bytes()
    mock_diagnosis = DiagnosisExplanation(
        thinking="Visual indicators are consistent with Brown Spot. Suggesting treatment.",
        explanation="Brown Spot is a fungal disease that can be treated.",
        recommendation="Apply balanced fertilizer.",
        severity="medium",
    )

    from app.main import app

    # Temporarily patch settings.openai_api_key and the explainer.explain method
    with patch.object(app.state.settings, "openai_api_key", "sk-mock-api-key-test"):
        with patch.object(app.state.explainer, "explain", return_value=mock_diagnosis) as mock_explain:
            response = await client.post(
                "/api/v1/detect",
                files={"file": ("leaf.png", image_bytes, "image/png")},
            )

            assert response.status_code == 200
            data = response.json()
            assert data["thinking"] == "Visual indicators are consistent with Brown Spot. Suggesting treatment."
            assert data["explanation"] == "Brown Spot is a fungal disease that can be treated."
            assert data["recommendation"] == "Apply balanced fertilizer."
            assert data["severity"] == "medium"
            mock_explain.assert_called_once()


@pytest.mark.asyncio
async def test_detect_endpoint_graceful_fallback_on_llm_failure(client: AsyncClient):
    """Detection endpoint should still succeed and return fallback values if the LLM call fails."""
    image_bytes = _create_test_image_bytes()

    from app.main import app

    # Patch settings.openai_api_key to be True, and mock explain to raise an exception
    with patch.object(app.state.settings, "openai_api_key", "sk-mock-api-key-test"):
        with patch.object(app.state.explainer, "explain", side_effect=RuntimeError("OpenAI API error")):
            response = await client.post(
                "/api/v1/detect",
                files={"file": ("leaf.png", image_bytes, "image/png")},
            )

            assert response.status_code == 200
            data = response.json()
            assert "LLM error: OpenAI API error" in data["thinking"]
            assert data["explanation"] == "Diagnosis explanation is temporarily unavailable."
            assert data["recommendation"] == "Please consult an agricultural expert or try again later."
            assert data["severity"] == "unknown"
