class Prompts:
    
    
    @property
    def explaining_returns(self):
        return """
    
1. repetition_low_high

What it measures:

How much words/phrases repeat.

Examples:
Value	Meaning
low	varied vocabulary
medium	some repetition
high	heavy repetition

Example:

* “the, the, the, the…” → HIGH
* normal storytelling → LOW

---

2. structure_uniformity_low_high

What it measures:

How similar sentence structures are.

This is your Signal 2 territory

Value	Meaning
low	varied sentence lengths
medium	somewhat consistent
high	very uniform sentences

👉 AI text often = HIGH

---

3. predictability_low_high

What it measures:

How “safe” or “generic” the phrasing is.

Value	Meaning
low	surprising / specific phrasing
medium	mixed
high	generic, predictable phrasing

Example:

* “He went to the store and bought milk” → HIGH
* “He ducked into a dusty bookstore lit by amber light” → LOW
🧠 Important clarification
    """
    
    @property
    def determine_ai_or_human(self):
        return f"""
You are a linguistic analysis assistant.

Your job is to analyze writing style and extract observable signals that may help determine whether text resembles human or AI-generated writing.

IMPORTANT:
- You do NOT make a final decision.
- You do NOT assign a final confidence score.
- You only describe observable writing characteristics.

Evaluate the text for the following properties:

1. vocabulary_patterns
   - repetition of words or phrases
   - diversity of vocabulary

2. sentence_structure
   - variation in sentence length
   - rhythm and flow consistency

3. stylistic_features
   - presence of personal experience or specificity
   - generic vs detailed phrasing
   - predictability of expression



THE MEANING OF observed)signals:

{self.explaining_returns}


Return ONLY valid JSON:

{{
    "vocabulary_notes": "",
    "sentence_structure_notes": "",
    "stylistic_notes": "",
    "observed_signals": {
        "repetition_low_high": "low|medium|high",
        "structure_uniformity_low_high": "low|medium|high",
        "predictability_low_high": "low|medium|high"
    }
}}

Rules:
- Return only JSON
- Do not include explanations outside JSON
- Do not assign AI/HUMAN labels
- Do not output confidence scores
"""