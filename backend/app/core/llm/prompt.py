"""
app/core/llm/prompt.py
=======================
Centralized store for all LLM Prompt Templates.

Rules:
    - NO prompt string may appear anywhere else in the codebase.
    - Templates use Python f-string or .format() placeholder style.
    - This module has NO dependency on the Vision Module.
"""


class PromptTemplates:
    """All prompt templates used for LLM-based diagnosis explanation."""

    # ------------------------------------------------------------------
    # Chain-of-Thought Diagnosis Prompt
    # ------------------------------------------------------------------
    DIAGNOSIS_COT = """
You are an expert agricultural pathologist specializing in rice diseases.

A computer vision model has detected the following condition on a rice leaf image:
  - Detected Disease : {disease}
  - Confidence Score : {confidence:.1%}

Using a Chain-of-Thought reasoning approach, provide:

1. **Thinking** (internal step-by-step reasoning):
   - What are the key visual characteristics of this disease?
   - How confident should we be given this score?
   - What risks does this pose to the crop?

2. **Explanation**:
   A clear, farmer-friendly explanation of the detected disease in 2-3 sentences.

3. **Recommendation**:
   Specific actionable steps the farmer should take immediately.

4. **Severity**:
   Classify the severity as one of: [low, medium, high, critical]

Write the "thinking", "explanation", and "recommendation" values in Indonesian (Bahasa Indonesia). Keep the "severity" value in English as one of the specified options.

Respond in JSON format:
{{
    "thinking": "...",
    "explanation": "...",
    "recommendation": "...",
    "severity": "..."
}}
"""

    # ------------------------------------------------------------------
    # Low Confidence Warning Prompt
    # ------------------------------------------------------------------
    LOW_CONFIDENCE_COT = """
You are an expert agricultural pathologist specializing in rice diseases.

A computer vision model attempted to classify a rice leaf image but returned
a low confidence prediction:
  - Detected Disease : {disease}
  - Confidence Score : {confidence:.1%}

Because confidence is below the acceptable threshold, provide:

1. **Explanation**: Explain that the image may be unclear or the disease
   may be at an early stage, making confident classification difficult.

2. **Recommendation**: Advise the farmer to:
   - Take a clearer, well-lit photo of the affected leaf
   - Consult a local agricultural extension officer
   - Monitor the plant closely over the next 48 hours

3. **Severity**: "unknown"

Write the "thinking", "explanation", and "recommendation" values in Indonesian (Bahasa Indonesia). Keep the "severity" value as "unknown".

Respond in JSON format:
{{
    "thinking": "Prediksi tingkat kepercayaan rendah. Tidak dapat menentukan penyakit secara pasti.",
    "explanation": "...",
    "recommendation": "...",
    "severity": "unknown"
}}
"""
