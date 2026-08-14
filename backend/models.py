from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey
from .database import Base


# INDUSTRY
class Industry(Base):
    __tablename__ = "industries"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(200),
        nullable=False,
        unique=True
    )

    description = Column(Text)


# VALUE CHAIN STAGE
class ValueChainStage(Base):
    __tablename__ = "value_chain_stages"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # Each stage belongs to an industry
    industry_id = Column(
        Integer,
        ForeignKey("industries.id"),
        nullable=True
    )

    name = Column(
        String(200),
        nullable=False
    )

    description = Column(Text)


# PROCESS
class Process(Base):
    __tablename__ = "processes"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # Process belongs to a value-chain stage
    stage_id = Column(
        Integer,
        ForeignKey("value_chain_stages.id")
    )

    name = Column(
        String(200),
        nullable=False
    )

    description = Column(Text)

    # AI Analysis
    business_problem = Column(Text)

    ai_opportunity = Column(Text)

    ai_capability = Column(
        String(300)
    )

    expected_benefit = Column(Text)

    risk = Column(Text)


    # Priority Analysis
    value_score = Column(Float)

    feasibility_score = Column(Float)

    risk_score = Column(Float)

    confidence_score = Column(Float)

    priority_score = Column(Float)

    priority_level = Column(
        String(50)
    )


# RESEARCH SOURCE
class ResearchSource(Base):
    __tablename__ = "research_sources"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    # Research belongs to a process
    process_id = Column(
        Integer,
        ForeignKey("processes.id")
    )

    title = Column(
        String(500)
    )

    source_type = Column(
        String(100)
    )

    url = Column(
        String(1000)
    )

    evidence = Column(Text)