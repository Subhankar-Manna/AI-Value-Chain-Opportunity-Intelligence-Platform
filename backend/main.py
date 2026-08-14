from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .database import get_db
from .models import (
    Industry,
    ValueChainStage,
    Process,
    ResearchSource
)

from ai.analyzer import analyze_process
from ai.priority import calculate_priority
from ai.industry_builder import build_industry

# REQUEST MODELS
class ProcessCreate(BaseModel):

    stage_id: int

    name: str

    description: str


class IndustryCreate(BaseModel):

    industry: str


# FASTAPI APPLICATION
app = FastAPI(

    title="AI Value Chain Opportunity Intelligence API",

    description=(
        "Backend API for analysing AI opportunities "
        "across multiple industries."
    ),

    version="1.0.0"
)


# ROOT
@app.get("/")
def root():

    return {

        "message":
        "AI Value Chain Opportunity Intelligence API is running"

    }


# HEALTH CHECK
@app.get("/health")
def health():

    return {

        "status": "healthy"

    }

# GET ALL INDUSTRIES
@app.get("/industries")
def get_industries(

    db: Session = Depends(get_db)

):

    industries = db.query(
        Industry
    ).all()

    return [

        {

            "id": industry.id,

            "name": industry.name,

            "description": industry.description

        }

        for industry in industries

    ]

# BUILD INDUSTRY USING AI
@app.post("/industries/build")
def create_industry(

    industry_data: IndustryCreate,

    db: Session = Depends(get_db)

):

   
    # Validate industry name
    industry_name = (
        industry_data.industry or ""
    ).strip()

    if not industry_name:

        raise HTTPException(

            status_code=400,

            detail="Industry name cannot be empty"

        )


    # Check whether industry already exists
    existing_industry = db.query(
        Industry
    ).filter(

        Industry.name.ilike(
            industry_name
        )

    ).first()


    if existing_industry:

        return {

            "message":
            "Industry already exists",

            "industry_id":
            existing_industry.id,

            "industry":
            existing_industry.name

        }

    # Generate value chain using Qwen
    try:

        result = build_industry(
            industry_name
        )

    except Exception as e:

        raise HTTPException(

            status_code=500,

            detail=(
                "Industry generation failed: "
                f"{str(e)}"
            )

        )

    # Create Industry
    try:

        industry = Industry(

            name=result["industry"],

            description=(
                "AI-generated value chain for the "
                f"{result['industry']} industry."
            )

        )

        db.add(industry)

        db.flush()


        # Create stages and processes
        created_stages = []


        for stage_data in result["stages"]:

            stage = ValueChainStage(

                industry_id=industry.id,

                name=stage_data["stage_name"],

                description=(
                    stage_data["stage_description"]
                )

            )

            db.add(stage)

            db.flush()


            created_processes = []


            for process_data in stage_data["processes"]:

                process = Process(

                    stage_id=stage.id,

                    name=(
                        process_data["process_name"]
                    ),

                    description=(
                        process_data["process_description"]
                    )

                )

                db.add(process)


                created_processes.append({

                    "name":
                    process_data["process_name"],

                    "description":
                    process_data["process_description"]

                })


            created_stages.append({

                "name":
                stage_data["stage_name"],

                "description":
                stage_data["stage_description"],

                "processes":
                created_processes

            })


        # ------------------------------------------
        # 6. Save everything
        # ------------------------------------------

        db.commit()

        db.refresh(industry)


    except Exception as e:

        db.rollback()

        raise HTTPException(

            status_code=500,

            detail=(
                "Database error while creating "
                f"industry: {str(e)}"
            )

        )


    # ----------------------------------------------
    # 7. Return generated value chain
    # ----------------------------------------------

    return {

        "message":
        "Industry value chain created successfully",

        "industry": {

            "id":
            industry.id,

            "name":
            industry.name,

            "description":
            industry.description

        },

        "stages":
        created_stages

    }


# GET ALL VALUE-CHAIN STAGES
@app.get("/stages")
def get_stages(

    db: Session = Depends(get_db)

):

    stages = db.query(
        ValueChainStage
    ).all()


    return [

        {

            "id":
            stage.id,

            "industry_id":
            stage.industry_id,

            "name":
            stage.name,

            "description":
            stage.description

        }

        for stage in stages

    ]


# GET ALL PROCESSES
@app.get("/processes")
def get_processes(

    db: Session = Depends(get_db)

):

    processes = db.query(
        Process
    ).all()


    return [

        {

            "id":
            process.id,

            "stage_id":
            process.stage_id,

            "name":
            process.name,

            "description":
            process.description,


            # --------------------------------------
            # AI Analysis
            # --------------------------------------

            "business_problem":
            process.business_problem,

            "ai_opportunity":
            process.ai_opportunity,

            "ai_capability":
            process.ai_capability,

            "expected_benefit":
            process.expected_benefit,

            "risk":
            process.risk,

            # Priority
            "value_score":
            process.value_score,

            "feasibility_score":
            process.feasibility_score,

            "risk_score":
            process.risk_score,

            "confidence_score":
            process.confidence_score,

            "priority_score":
            process.priority_score,

            "priority_level":
            process.priority_level

        }

        for process in processes

    ]


# CREATE NEW PROCESS
@app.post("/processes")
def create_process(

    process_data: ProcessCreate,

    db: Session = Depends(get_db)

):

  
    # Check whether stage exists
    stage = db.query(
        ValueChainStage
    ).filter(

        ValueChainStage.id ==
        process_data.stage_id

    ).first()


    if not stage:

        raise HTTPException(

            status_code=404,

            detail=
            "Value chain stage not found"

        )

    # Validate process name
    process_name = (
        process_data.name or ""
    ).strip()


    if not process_name:

        raise HTTPException(

            status_code=400,

            detail=
            "Process name cannot be empty"

        )


    # Create process
    process = Process(

        stage_id=process_data.stage_id,

        name=process_name,

        description=(
            process_data.description or ""
        ).strip()

    )

    db.add(process)


    # Save process
    db.commit()

    db.refresh(process)


    # Return created process
    return {

        "message":
        "Process created successfully",

        "process": {

            "id":
            process.id,

            "stage_id":
            process.stage_id,

            "name":
            process.name,

            "description":
            process.description

        }

    }


# GET SINGLE PROCESS
@app.get("/processes/{process_id}")
def get_process(

    process_id: int,

    db: Session = Depends(get_db)

):

    process = db.query(
        Process
    ).filter(

        Process.id == process_id

    ).first()


    if not process:

        raise HTTPException(

            status_code=404,

            detail="Process not found"

        )


    return {

        "id":
        process.id,

        "stage_id":
        process.stage_id,

        "name":
        process.name,

        "description":
        process.description,


        # AI Analysis
        "business_problem":
        process.business_problem,

        "ai_opportunity":
        process.ai_opportunity,

        "ai_capability":
        process.ai_capability,

        "expected_benefit":
        process.expected_benefit,

        "risk":
        process.risk,


        # Priority
        "value_score":
        process.value_score,

        "feasibility_score":
        process.feasibility_score,

        "risk_score":
        process.risk_score,

        "confidence_score":
        process.confidence_score,

        "priority_score":
        process.priority_score,

        "priority_level":
        process.priority_level

    }


# AI ANALYSIS + PRIORITY + RESEARCH
@app.post("/analyze/{process_id}")
def analyze_retail_process(

    process_id: int,

    db: Session = Depends(get_db)

):


    # FIND PROCESS
    process = db.query(
        Process
    ).filter(

        Process.id == process_id

    ).first()


    if not process:

        raise HTTPException(

            status_code=404,

            detail="Process not found"

        )

    # VALIDATE PROCESS INFORMATION
    process_name = (
        process.name or ""
    ).strip()


    process_description = (
        process.description or ""
    ).strip()


    if not process_name:

        raise HTTPException(

            status_code=400,

            detail="Process name is missing"

        )

    # FIND VALUE-CHAIN STAGE
    stage = db.query(
        ValueChainStage
    ).filter(

        ValueChainStage.id ==
        process.stage_id

    ).first()


    if not stage:

        raise HTTPException(

            status_code=404,

            detail=
            "Value chain stage not found for this process"

        )


    stage_name = (
        stage.name or ""
    ).strip()


    # FIND INDUSTRY
    industry_name = ""


    if stage.industry_id is not None:

        industry = db.query(
            Industry
        ).filter(

            Industry.id ==
            stage.industry_id

        ).first()


        if industry:

            industry_name = (
                industry.name or ""
            ).strip()


    if not industry_name:

        industry_name = "Retail"


   
    # AI ANALYSIS USING QWEN
    try:

        result = analyze_process(

            process_name=
            process_name,

            process_description=
            process_description,

            industry=
            industry_name,

            stage_name=
            stage_name

        )


    except TypeError as e:

        raise HTTPException(

            status_code=500,

            detail=(
                "AI analyzer function signature "
                "mismatch. Expected "
                "analyze_process("
                "process_name, "
                "process_description, "
                "industry, "
                "stage_name"
                "). "
                f"Error: {str(e)}"
            )

        )


    except Exception as e:

        raise HTTPException(

            status_code=500,

            detail=
            f"AI analysis failed: {str(e)}"

        )


    # SAVE AI ANALYSIS
    try:

        process.business_problem = (
            result["business_problem"]
        )


        process.ai_opportunity = (
            result["ai_opportunity"]
        )


        process.ai_capability = (
            result["ai_capability"]
        )


        process.expected_benefit = (
            result["expected_benefit"]
        )


        process.risk = (
            result["risk"]
        )


        # CALCULATE PRIORITY
        priority = calculate_priority(

            value_score=
            result["value_score"],

            feasibility_score=
            result["feasibility_score"],

            risk_score=
            result["risk_score"],

            confidence_score=
            result["confidence_score"]

        )

        # SAVE PRIORITY INFORMATION
        process.value_score = (
            priority["value_score"]
        )


        process.feasibility_score = (
            priority["feasibility_score"]
        )


        process.risk_score = (
            priority["risk_score"]
        )


        process.confidence_score = (
            priority["confidence_score"]
        )


        process.priority_score = (
            priority["priority_score"]
        )


        process.priority_level = (
            priority["priority_level"]
        )

        # SAVE / UPDATE RESEARCH EVIDENCE
        research_title = (
            result.get("research_title")
            or f"AI Applications in {process_name}"
        )


        research_source_type = (
            result.get("research_source_type")
            or "Research / Industry"
        )


        research_evidence = (
            result.get("research_evidence")
            or (
                f"AI techniques can support "
                f"{process_name.lower()} by improving "
                f"analysis, decision making and "
                f"process efficiency."
            )
        )


        # Check whether research already exists
        research_source = db.query(
            ResearchSource
        ).filter(

            ResearchSource.process_id ==
            process.id

        ).first()


        if research_source:

            # Update existing research
            research_source.title = (
                research_title
            )

            research_source.source_type = (
                research_source_type
            )

            research_source.evidence = (
                research_evidence
            )

        else:

        
            # Create new research source
            research_source = ResearchSource(

                process_id=
                process.id,

                title=
                research_title,

                source_type=
                research_source_type,

                url=None,

                evidence=
                research_evidence

            )

            db.add(
                research_source
            )


        # SAVE EVERYTHING
        db.commit()

        db.refresh(process)

        if research_source:

            db.refresh(
                research_source
            )


    except KeyError as e:

        db.rollback()

        raise HTTPException(

            status_code=500,

            detail=(
                "AI response missing "
                f"required field: {str(e)}"
            )

        )


    except Exception as e:

        db.rollback()

        raise HTTPException(

            status_code=500,

            detail=(
                "Failed to save AI analysis "
                f"or research: {str(e)}"
            )

        )

    # RETURN COMPLETE ANALYSIS
    return {

        "process_id":
        process.id,

        "process_name":
        process.name,

        "industry":
        industry_name,

        "stage":
        stage_name,


        # AI Analysis
        "analysis": {

            "business_problem":
            process.business_problem,

            "ai_opportunity":
            process.ai_opportunity,

            "ai_capability":
            process.ai_capability,

            "expected_benefit":
            process.expected_benefit,

            "risk":
            process.risk

        },



        # Priority
        "priority": {

            "value_score":
            process.value_score,

            "feasibility_score":
            process.feasibility_score,

            "risk_score":
            process.risk_score,

            "confidence_score":
            process.confidence_score,

            "priority_score":
            process.priority_score,

            "priority_level":
            process.priority_level

        },


        # Research
        "research": {

            "title":
            research_source.title,

            "source_type":
            research_source.source_type,

            "url":
            research_source.url,

            "evidence":
            research_source.evidence

        }

    }


# GET RESEARCH / EVIDENCE
@app.get("/research/{process_id}")
def get_research(

    process_id: int,

    db: Session = Depends(get_db)

):

    # CHECK WHETHER PROCESS EXISTS
    process = db.query(
        Process
    ).filter(

        Process.id == process_id

    ).first()


    if not process:

        raise HTTPException(

            status_code=404,

            detail="Process not found"

        )


    # GET RESEARCH SOURCES FOR THIS PROCESS
    sources = db.query(
        ResearchSource
    ).filter(

        ResearchSource.process_id ==
        process_id

    ).all()


    # RETURN RESEARCH EVIDENCE
    return [

        {

            "id":
            source.id,

            "process_id":
            source.process_id,

            "title":
            source.title,

            "source_type":
            source.source_type,

            "url":
            source.url,

            "evidence":
            source.evidence

        }

        for source in sources

    ]