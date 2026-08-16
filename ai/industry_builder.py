import json
from google import genai
from google.genai import types

MODEL_NAME = "gemini-3.5-flash"


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


# Create Gemini client.
# The client automatically reads GEMINI_API_KEY
# from the environment.
client = genai.Client()


def build_industry(industry_name: str):

    # Clean user input
    industry_name = (industry_name or "").strip()

    if not industry_name:
        raise ValueError(
            "Industry name cannot be empty."
        )

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

    try:

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=INDUSTRY_SCHEMA,
                temperature=0.2
            )
        )

        content = response.text

        if not content:
            raise ValueError(
                "Gemini returned an empty response."
            )

        result = json.loads(content)

    except json.JSONDecodeError as e:

        raise ValueError(
            f"Gemini returned invalid JSON: {str(e)}"
        )

    except Exception as e:

        raise RuntimeError(
            f"Gemini industry generation failed: {str(e)}"
        )

    # Make sure the returned industry is present
    if not result.get("industry"):
        result["industry"] = industry_name

    # Validate stages
    if "stages" not in result:
        raise ValueError(
            "AI response does not contain value-chain stages."
        )

    if not isinstance(result["stages"], list):
        raise ValueError(
            "Invalid stages format returned by AI."
        )

    return result

