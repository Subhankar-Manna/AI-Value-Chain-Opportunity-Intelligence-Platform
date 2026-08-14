from backend.database import SessionLocal, engine, Base
from backend.models import ValueChainStage, Process

Base.metadata.create_all(bind=engine)

db = SessionLocal()


stages = [
    {
        "name": "Supplier & Procurement",
        "description": "Activities related to supplier selection, purchasing and supplier management."
    },
    {
        "name": "Inbound Logistics",
        "description": "Movement and receiving of products from suppliers."
    },
    {
        "name": "Inventory Management",
        "description": "Activities related to forecasting, tracking and replenishing inventory."
    },
    {
        "name": "Store Operations",
        "description": "Daily activities required to operate retail stores."
    },
    {
        "name": "Marketing & Customer Engagement",
        "description": "Activities related to customer analysis, marketing and personalisation."
    },
    {
        "name": "Sales & Checkout",
        "description": "Activities related to selling products and processing transactions."
    },
    {
        "name": "After-Sales & Customer Service",
        "description": "Activities related to customer support, returns and feedback."
    }
]


stage_objects = []

for stage_data in stages:
    stage = ValueChainStage(**stage_data)
    db.add(stage)
    stage_objects.append(stage)

db.commit()


processes = [
    ("Supplier & Procurement", "Supplier Selection"),
    ("Supplier & Procurement", "Purchase Planning"),
    ("Supplier & Procurement", "Supplier Evaluation"),

    ("Inbound Logistics", "Delivery Tracking"),

    ("Inventory Management", "Demand Forecasting"),
    ("Inventory Management", "Stock Replenishment"),

    ("Store Operations", "Staff Scheduling"),
    ("Store Operations", "Shelf Monitoring"),

    ("Marketing & Customer Engagement", "Customer Segmentation"),

    ("After-Sales & Customer Service", "Customer Support"),
]


for stage_name, process_name in processes:

    stage = db.query(ValueChainStage).filter(
        ValueChainStage.name == stage_name
    ).first()

    process = Process(
        stage_id=stage.id,
        name=process_name,
        description=f"Retail process related to {process_name.lower()}."
    )

    db.add(process)


db.commit()
db.close()

print("Retail seed data inserted successfully!")