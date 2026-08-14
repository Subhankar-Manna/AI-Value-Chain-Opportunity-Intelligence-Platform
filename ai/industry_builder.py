import json
import ollama


MODEL_NAME = "qwen2.5:1.5b"


INDUSTRY_SCHEMA = {
    "type": "object",
    "properties": {
        "industry": {
            "type": "string"
        },
        "stages": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "stage_name": {
                        "type": "string"
                    },
                    "stage_description": {
                        "type": "string"
                    },
                    "processes": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "process_name": {
                                    "type": "string"
                                },
                                "process_description": {
                                    "type": "string"
                                }
                            },
                            "required": [
                                "process_name",
                                "process_description"
                            ]
                        }
                    }
                },
                "required": [
                    "stage_name",
                    "stage_description",
                    "processes"
                ]
            }
        }
    },
    "required": [
        "industry",
        "stages"
    ]
}


def build_industry(industry_name: str):

    # Clean user input
    industry_name = industry_name.strip()

    if not industry_name:
        raise ValueError("Industry name cannot be empty.")

    prompt = f"""
You are an enterprise business transformation analyst.

The user wants to analyse this industry:

Industry:
{industry_name}

Construct a realistic end-to-end value chain for this industry.

Your task is to identify the major value-chain stages and the important
business processes within each stage.

The generated value chain will later be analysed for:

- Business problems
- AI opportunities
- AI capabilities
- Expected benefits
- Risks
- Priority

Requirements:

1. Generate 5 to 7 major value-chain stages.

2. Each stage should contain 2 to 4 important business processes.

3. Stages must cover the industry's end-to-end value chain.

4. Processes must represent realistic business activities.

5. Make the stages and processes specific to the selected industry.

6. Do not use generic retail-specific information.

7. Do not assume that the industry is Retail.

8. Use clear and concise business language.

9. Avoid duplicate stages and duplicate processes.

10. Do not generate explanations outside the JSON response.

11. Return ONLY valid JSON matching the required structure.

Selected Industry:
{industry_name}
"""

    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        format=INDUSTRY_SCHEMA
    )

    content = response["message"]["content"]

    try:
        result = json.loads(content)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"AI returned invalid JSON: {e}"
        )

    # Make sure the returned industry is present
    if not result.get("industry"):
        result["industry"] = industry_name

    # Basic validation
    if "stages" not in result:
        raise ValueError(
            "AI response does not contain value-chain stages."
        )

    if not isinstance(result["stages"], list):
        raise ValueError(
            "Invalid stages format returned by AI."
        )

    return result