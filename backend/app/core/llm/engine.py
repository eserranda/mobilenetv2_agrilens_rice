"""
app/core/llm/engine.py
=======================
Manages communication with the LLM provider (e.g. OpenAI).

This module abstracts the provider client so that the rest of the
codebase interacts with a single, consistent interface.

Note:
    This module is prepared for Phase 2 integration.
    In Phase 1 it is NOT called by any active code path.
    It has NO dependency on the Vision Module.
"""
import json
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class LLMEngine:
    """Client wrapper for interacting with an LLM provider API.

    Usage:
        engine = LLMEngine(api_key="sk-...", model="gpt-4o")
        response = engine.complete(prompt="Explain brown spot in rice...")
    """

    def __init__(self, api_key: str, model: str = "gpt-4o") -> None:
        self._api_key = api_key
        self._model = model
        self._client: Optional[Any] = None

        if api_key:
            self._initialize_client()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def complete(self, prompt: str, temperature: float = 0.3) -> str:
        """Send a prompt to the LLM and return the raw text response.

        Args:
            prompt: The full prompt string to send to the LLM.
            temperature: Sampling temperature (0.0 = deterministic).

        Returns:
            The LLM's text response.

        Raises:
            RuntimeError: If the LLM client is not initialized.
        """
        if not self._client:
            raise RuntimeError(
                "LLM client is not initialized. "
                "Ensure OPENAI_API_KEY is set in your .env file."
            )

        logger.info("Sending prompt to LLM | model=%s", self._model)

        response = self._client.chat.completions.create(
            model=self._model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content
        if content is None:
            raise ValueError("LLM returned an empty response.")
        return content

    def complete_json(self, prompt: str, temperature: float = 0.3) -> Dict:
        """Send a prompt and parse the response as JSON.

        Args:
            prompt: The full prompt string.
            temperature: Sampling temperature.

        Returns:
            Parsed JSON dict from the LLM response.

        Raises:
            ValueError: If the response cannot be parsed as JSON.
        """
        raw = self.complete(prompt, temperature)
        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"LLM returned invalid JSON: {exc}\nRaw response: {raw}"
            ) from exc

    # ------------------------------------------------------------------
    # Private Helpers
    # ------------------------------------------------------------------

    def _initialize_client(self) -> None:
        """Initialize the LLM provider SDK client."""
        logger.info("Initializing OpenAI client...")
        from openai import OpenAI
        self._client = OpenAI(api_key=self._api_key)
