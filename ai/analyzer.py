import json
import ollama


MODEL_NAME = "qwen2.5:1.5b"



# AI ANALYSIS SCHEMA

ANALYSIS_SCHEMA = {
    "type": "object",
    "properties": {

        "business_problem": {
            "type": "string"
        },

        "ai_opportunity": {
            "type": "string"
        },

        "ai_capability": {
            "type": "string"
        },

        "expected_benefit": {
            "type": "string"
        },

        "risk": {
            "type": "string"
        },

        "value_score": {
            "type": "number"
        },

        "feasibility_score": {
            "type": "number"
        },

        "risk_score": {
            "type": "number"
        },

        "confidence_score": {
            "type": "number"
        },

        # Research Evidence

        "research_title": {
            "type": "string"
        },

        "research_source_type": {
            "type": "string"
        },

        "research_evidence": {
            "type": "string"
        }
    },

    "required": [
        "business_problem",
        "ai_opportunity",
        "ai_capability",
        "expected_benefit",
        "risk",

        "value_score",
        "feasibility_score",
        "risk_score",
        "confidence_score",

        "research_title",
        "research_source_type",
        "research_evidence"
    ]
}


# ==================================================
# ANALYZE PROCESS
# ==================================================

def analyze_process(
    process_name: str,
    process_description: str,
    industry: str = "",
    stage_name: str = ""
):
    """
    Analyse a value-chain process using the local Qwen model.

    The function generates:

    - Business problem
    - AI opportunity
    - AI capability
    - Expected benefit
    - Risk
    - Priority-related scores
    - Research evidence/context

    Parameters:
        process_name:
            Name of the business process.

        process_description:
            Description of the business process.

        industry:
            Industry to which the process belongs.

        stage_name:
            Value-chain stage containing the process.
    """



    process_name = (
        process_name or ""
    ).strip()

    process_description = (
        process_description or ""
    ).strip()

    industry_context = (
        industry.strip()
        if industry
        else "the selected industry"
    )

    stage_context = (
        stage_name.strip()
        if stage_name
        else "the relevant value-chain stage"
    )



    # VALIDATION

    if not process_name:

        raise ValueError(
            "Process name cannot be empty."
        )


    

    prompt = f"""
You are an enterprise AI transformation analyst.

Analyse the following business process as part of a
multi-industry value-chain intelligence system.

Industry:
{industry_context}

Value Chain Stage:
{stage_context}

Process:
{process_name}

Process Description:
{process_description}


Your task is to identify realistic opportunities where
AI can create measurable business value in this process.


==================================================
PART 1 — BUSINESS ANALYSIS
==================================================

1. business_problem

Explain the main business problem, inefficiency,
bottleneck, cost, delay, quality issue, forecasting
problem, or decision-making challenge associated
with this process.

Keep the explanation concise.


2. ai_opportunity

Explain how AI could realistically improve this process.

Do not force AI into the process if there is no realistic
business use case.


3. ai_capability

Identify the main AI capability required.

Possible examples:

- Predictive Analytics
- Machine Learning
- Computer Vision
- Natural Language Processing
- Generative AI
- Recommendation Systems
- Forecasting
- Anomaly Detection
- Optimization
- Intelligent Automation


4. expected_benefit

Describe the expected business benefits.

Possible benefits include:

- cost reduction
- faster processing
- improved quality
- better forecasting
- improved customer experience
- reduced errors
- increased productivity
- improved decision making


5. risk

Describe important implementation risks.

Possible risks include:

- data quality
- privacy
- security
- model accuracy
- regulatory requirements
- integration complexity
- human oversight
- adoption challenges


==================================================
PART 2 — PRIORITY SCORES
==================================================

Provide four numerical scores from 1 to 10.


6. value_score

How valuable would AI be for this process?

1 = very low value
10 = very high value


7. feasibility_score

How feasible is AI implementation for this process?

1 = very difficult
10 = very easy


8. risk_score

How risky is AI implementation?

1 = very low risk
10 = very high risk


9. confidence_score

How confident are you in this assessment?

1 = very low confidence
10 = very high confidence.


==================================================
PART 3 — RESEARCH EVIDENCE
==================================================

Provide a short research-oriented evidence summary
that supports the identified AI opportunity.

The evidence must be directly related to:

Industry:
{industry_context}

Stage:
{stage_context}

Process:
{process_name}


10. research_title

Create a concise title describing the AI application
or research topic relevant to this process.

Example:

"AI Applications in Healthcare Patient Assessment"


11. research_source_type

Use a suitable category such as:

- Research / Industry
- AI Research
- Industry Practice
- Technology Research
- Business Research


12. research_evidence

Write 1–3 sentences explaining how AI techniques
are relevant to this process.

The evidence should be specific to the selected
industry and process.

Do not invent statistics, percentages, research
paper names, authors, or factual claims that cannot
be reasonably supported.

Do not pretend that this text comes from a specific
published paper.

This field represents research-oriented supporting
context for the AI opportunity.


==================================================
IMPORTANT RULES
==================================================

- Use the actual industry provided.
- Use the actual value-chain stage provided.
- Use the actual process provided.
- Do not assume the industry is Retail.
- Do not generate Retail-specific information for
  Healthcare, Automotive, Manufacturing, etc.
- Do not force Generative AI into every process.
- Use different and realistic scores for different
  processes.
- Avoid duplicate or generic explanations.
- Keep all explanations concise.
- Use professional enterprise language.
- Return ONLY valid JSON.
- Do not include Markdown.
- Do not include explanations outside the JSON.
"""


    # CALL QWEN
    try:

        response = ollama.chat(
            model=MODEL_NAME,

            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            format=ANALYSIS_SCHEMA
        )

        content = response["message"]["content"]

        result = json.loads(content)

    except json.JSONDecodeError as e:

        raise RuntimeError(
            f"Ollama returned invalid JSON: {str(e)}"
        )

    except Exception as e:

        raise RuntimeError(
            f"Ollama AI analysis failed: {str(e)}"
        )


    # VALIDATE REQUIRED TEXT FIELDS
    text_fields = [
        "business_problem",
        "ai_opportunity",
        "ai_capability",
        "expected_benefit",
        "risk",
        "research_title",
        "research_source_type",
        "research_evidence"
    ]

    for field in text_fields:

        if field not in result:

            result[field] = ""

        elif result[field] is None:

            result[field] = ""

        else:

            result[field] = str(
                result[field]
            ).strip()

    # VALIDATE AND NORMALIZE SCORES
    score_fields = [
        "value_score",
        "feasibility_score",
        "risk_score",
        "confidence_score"
    ]

    for field in score_fields:

        try:

            score = float(
                result[field]
            )

        except (
            KeyError,
            TypeError,
            ValueError
        ):

            score = 5.0

        # Keep score between 1 and 10
        score = max(
            1.0,
            min(10.0, score)
        )

        # Keep one decimal place
        result[field] = round(
            score,
            1
        )


    # FALLBACK RESEARCH TITLE
    if not result["research_title"]:

        result["research_title"] = (
            f"AI Applications in {process_name}"
        )


    # FALLBACK SOURCE TYPE
    if not result["research_source_type"]:

        result["research_source_type"] = (
            "Research / Industry"
        )


    # FALLBACK RESEARCH EVIDENCE
    if not result["research_evidence"]:

        result["research_evidence"] = (
            f"AI techniques can be applied to "
            f"{process_name.lower()} to support better "
            f"analysis, decision making and process "
            f"efficiency within the {industry_context} industry."
        )


    return result