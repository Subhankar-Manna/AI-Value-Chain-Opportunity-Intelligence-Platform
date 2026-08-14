from backend.database import SessionLocal
from backend.models import Process, ResearchSource


RESEARCH_DATA = {

    "Supplier Selection": {
        "title": "AI for Supplier Selection",
        "source_type": "Research / Industry",
        "url": "https://www.ibm.com/think/topics/ai-supply-chain",
        "evidence": (
            "AI can support supplier selection by analysing supplier "
            "performance, costs, quality, delivery history and other "
            "relevant procurement data."
        )
    },

    "Purchase Planning": {
        "title": "AI in Procurement and Purchase Planning",
        "source_type": "Research / Industry",
        "url": "https://www.ibm.com/think/topics/ai-supply-chain",
        "evidence": (
            "AI can analyse purchasing patterns, supplier information "
            "and demand signals to support procurement planning and "
            "improve purchasing decisions."
        )
    },

    "Supplier Evaluation": {
        "title": "AI for Supplier Performance Evaluation",
        "source_type": "Research / Industry",
        "url": "https://www.ibm.com/think/topics/ai-supply-chain",
        "evidence": (
            "AI can evaluate supplier performance using historical "
            "delivery, quality, cost and reliability information."
        )
    },

    "Delivery Tracking": {
        "title": "AI in Logistics and Delivery Tracking",
        "source_type": "Research / Industry",
        "url": "https://www.ibm.com/think/topics/ai-supply-chain",
        "evidence": (
            "AI can analyse shipment and logistics data to improve "
            "delivery tracking, identify delays and support more "
            "accurate delivery predictions."
        )
    },

    "Demand Forecasting": {
        "title": "AI Applications in Retail Demand Forecasting",
        "source_type": "Research / Industry",
        "url": "https://www.ibm.com/think/topics/ai-demand-forecasting",
        "evidence": (
            "AI demand forecasting can use historical sales data "
            "and other relevant factors to improve demand prediction "
            "and support better inventory planning."
        )
    },

    "Stock Replenishment": {
        "title": "AI for Inventory Replenishment",
        "source_type": "Research / Industry",
        "url": "https://www.ibm.com/think/topics/ai-supply-chain",
        "evidence": (
            "AI can use inventory levels, demand forecasts and supply "
            "information to recommend appropriate stock replenishment "
            "decisions."
        )
    },

    "Staff Scheduling": {
        "title": "AI for Workforce Scheduling",
        "source_type": "Research / Industry",
        "url": "https://www.ibm.com/think/topics/ai-workforce",
        "evidence": (
            "AI can analyse staffing requirements, employee availability "
            "and workload patterns to support more efficient workforce "
            "scheduling."
        )
    },

    "Shelf Monitoring": {
        "title": "Computer Vision for Retail Shelf Monitoring",
        "source_type": "Research / Industry",
        "url": "https://www.ibm.com/think/topics/computer-vision",
        "evidence": (
            "Computer vision can analyse store images to identify "
            "product availability, shelf conditions and potential "
            "stocking issues."
        )
    },

    "Customer Segmentation": {
        "title": "AI for Customer Segmentation",
        "source_type": "Research / Industry",
        "url": "https://www.ibm.com/think/topics/customer-analytics",
        "evidence": (
            "AI can analyse customer behaviour and transaction data "
            "to identify meaningful customer groups and support "
            "more targeted engagement."
        )
    },

    "Customer Support": {
        "title": "AI for Customer Service",
        "source_type": "Research / Industry",
        "url": "https://www.ibm.com/think/topics/ai-customer-service",
        "evidence": (
            "AI-powered customer service can analyse customer requests "
            "and provide automated assistance while helping service "
            "teams handle common support queries."
        )
    }
}


def update_research():

    db = SessionLocal()

    try:

        processes = db.query(Process).all()

        updated_count = 0
        created_count = 0

        for process in processes:

            research = RESEARCH_DATA.get(process.name)

            if not research:
                print(
                    f"Skipping process without research mapping: "
                    f"{process.name}"
                )
                continue

            # Check whether research already exists
            source = db.query(ResearchSource).filter(
                ResearchSource.process_id == process.id
            ).first()

            if source:

                # Update existing research
                source.title = research["title"]
                source.source_type = research["source_type"]
                source.url = research["url"]
                source.evidence = research["evidence"]

                updated_count += 1

            else:

                # Create research for processes that have none
                source = ResearchSource(
                    process_id=process.id,
                    title=research["title"],
                    source_type=research["source_type"],
                    url=research["url"],
                    evidence=research["evidence"]
                )

                db.add(source)

                created_count += 1

        db.commit()

        print("Research update completed successfully!")
        print(f"Existing research updated: {updated_count}")
        print(f"New research sources created: {created_count}")

    except Exception as e:

        db.rollback()

        print("Error updating research:")
        print(e)

    finally:

        db.close()


if __name__ == "__main__":
    update_research()