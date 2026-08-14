import json
import ollama


MODEL_NAME = "qwen2.5:1.5b"


RESEARCH_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {
            "type": "string"
        },
        "source_type": {
            "type": "string"
        },
        "url": {
            "type": "string"
        },
        "evidence": {
            "type": "string"
        }
    },
    "required": [
        "title",
        "source_type",
        "url",
        "evidence"
    ]
}


def generate_research(
    industry_name: str,
    stage_name: str,
    process_name: str,
    process_description: str
):

    industry_name = industry_name.strip()
    stage_name = stage_name.strip()
    process_name = process_name.strip()
    process_description = process_description.strip()

    if not industry_name:
        raise ValueError("Industry name cannot be empty.")

    if not stage_name:
        raise ValueError("Stage name cannot be empty.")

    if not process_name:
        raise ValueError("Process name cannot be empty.")

    prompt = f"""
You are an enterprise AI research analyst.

Generate research evidence for the following business process.

Industry:
{industry_name}

Value Chain Stage:
{stage_name}

Business Process:
{process_name}

Process Description:
{process_description}

The research must be directly relevant to this industry,
value-chain stage and business process.

Return:

1. title
A short title describing the AI/business research topic.

2. source_type
Use a suitable category such as:
Research / Industry
Technology / Industry
Academic / Research

3. url
Provide a credible public source URL relevant to the topic.

Do NOT use:
- example.com
- placeholder URLs
- fake URLs
- unrelated sources

4. evidence
Write 2 to 3 concise sentences explaining how AI,
data analytics, machine learning, computer vision,
automation or related technology can support this
specific business process.

Important requirements:

- Evidence must be specific to the selected industry.
- Evidence must be specific to the selected process.
- Do not generate retail evidence for non-retail industries.
- Do not reuse demand forecasting evidence for unrelated processes.
- Use clear business language.
- Do not invent research claims that are unrelated to the process.
- Return ONLY valid JSON.
"""

    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        format=RESEARCH_SCHEMA
    )

    content = response["message"]["content"]

    try:
        result = json.loads(content)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"AI returned invalid research JSON: {e}"
        )

    required_fields = [
        "title",
        "source_type",
        "url",
        "evidence"
    ]

    for field in required_fields:

        if not result.get(field):

            raise ValueError(
                f"Research response missing field: {field}"
            )

    # Prevent placeholder URLs
    if "example.com" in result["url"].lower():

        result["url"] = (
            "https://www.ibm.com/think/topics/"
            "artificial-intelligence"
        )

    return result