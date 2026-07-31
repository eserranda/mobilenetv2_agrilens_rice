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

    def validate_rice_plant_image(self, image_bytes: bytes) -> Dict[str, Any]:
        """Validate if the provided image contains a rice plant using the Vision API.

        Returns a dict: {"is_rice_plant": bool, "reason": str}
        """
        import base64

        if not self._client:
            logger.warning("OpenAI client not initialized. Skipping guardrail check.")
            return {"is_rice_plant": True, "reason": "OpenAI not configured"}

        base64_image = base64.b64encode(image_bytes).decode('utf-8')

        prompt = (
            "You are an expert agricultural pathology assistant.\n"
            "Analyze the provided image and determine if it shows a rice plant (Oryza sativa) - "
            "this includes a rice leaf, stalk, grain, field, crop, or nursery seedling.\n"
            "Respond strictly in JSON format using this schema:\n"
            "{\n"
            "  \"is_rice_plant\": true or false,\n"
            "  \"reason\": \"A brief explanation in Indonesian. If it is a rice plant, state what parts are visible. If it is not, state what is actually visible instead (e.g. 'Gambar ini adalah kucing' or 'Gambar ini adalah wajah manusia').\"\n"
            "}"
        )

        try:
            logger.info("Sending image to LLM for guardrail validation check...")
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                response_format={"type": "json_object"},
                temperature=0.0,
            )

            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty response from LLM")

            res = json.loads(content)
            logger.info("Guardrail check result: %s", str(res))
            return {
                "is_rice_plant": bool(res.get("is_rice_plant", True)),
                "reason": str(res.get("reason", ""))
            }
        except Exception as exc:
            logger.error("Failed to perform image guardrail validation check: %s", str(exc))
            # Fail-open: do not block prediction if API has an error
            return {"is_rice_plant": True, "reason": "Guardrail check failed to execute"}

    # ------------------------------------------------------------------
    # Private Helpers
    # ------------------------------------------------------------------

    def _initialize_client(self) -> None:
        """Initialize the LLM provider SDK client."""
        logger.info("Initializing OpenAI client...")
        from openai import OpenAI
        self._client = OpenAI(api_key=self._api_key)
