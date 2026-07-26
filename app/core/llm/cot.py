"""
app/core/llm/cot.py
====================
Translates a classification result into a structured Chain-of-Thought
diagnosis explanation using the LLM engine.

Responsibilities:
    - Format the appropriate prompt template based on confidence level
    - Invoke the LLM engine
    - Parse and return the structured explanation

This module has NO dependency on the Vision Module and does NOT
perform any image inference.

Note:
    Prepared for Phase 2. Not active in Phase 1.
"""
import logging
from dataclasses import dataclass

from app.core.llm.engine import LLMEngine
from app.core.llm.prompt import PromptTemplates

logger = logging.getLogger(__name__)

# Predictions below this threshold use the LOW_CONFIDENCE prompt
_LOW_CONFIDENCE_THRESHOLD = 0.60


@dataclass
class DiagnosisExplanation:
    """Structured output from the Chain-of-Thought explainer."""

    thinking: str
    explanation: str
    recommendation: str
    severity: str


class ChainOfThoughtExplainer:
    """Converts a prediction result into a human-readable diagnosis.

    The explainer selects the appropriate prompt template based on the
    confidence score and returns a structured explanation.

    Usage (Phase 2):
        explainer = ChainOfThoughtExplainer(engine)
        explanation = explainer.explain(disease="Brown Spot", confidence=0.97)
    """

    def __init__(self, engine: LLMEngine) -> None:
        self._engine = engine

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def explain(self, disease: str, confidence: float) -> DiagnosisExplanation:
        """Generate a CoT diagnosis explanation for a predicted disease.

        Args:
            disease: The predicted disease label (e.g. "Brown Spot").
            confidence: The confidence score from the predictor (0.0 - 1.0).

        Returns:
            A DiagnosisExplanation with explanation, recommendation, and severity.
        """
        prompt = self._build_prompt(disease, confidence)
        response = self._engine.complete_json(prompt)

        return DiagnosisExplanation(
            thinking=response.get("thinking", ""),
            explanation=response.get("explanation", ""),
            recommendation=response.get("recommendation", ""),
            severity=response.get("severity", "unknown"),
        )

    # ------------------------------------------------------------------
    # Private Helpers
    # ------------------------------------------------------------------

    def _build_prompt(self, disease: str, confidence: float) -> str:
        """Select and format the appropriate prompt template.

        Args:
            disease: Predicted disease label.
            confidence: Prediction confidence score.

        Returns:
            A formatted prompt string ready to send to the LLM.
        """
        if confidence < _LOW_CONFIDENCE_THRESHOLD:
            logger.info(
                "Using LOW_CONFIDENCE prompt | confidence=%.4f", confidence
            )
            return PromptTemplates.LOW_CONFIDENCE_COT.format(
                disease=disease,
                confidence=confidence,
            )

        logger.info(
            "Using DIAGNOSIS_COT prompt | disease=%s | confidence=%.4f",
            disease,
            confidence,
        )
        return PromptTemplates.DIAGNOSIS_COT.format(
            disease=disease,
            confidence=confidence,
        )
