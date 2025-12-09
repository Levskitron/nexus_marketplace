from app import app
from database import db
from models import Category

with app.app_context():

    categories = [
        ("PC Parts", None),
        ("CPU", "PC Parts"),
        ("GPU", "PC Parts"),
        ("Motherboard", "PC Parts"),
        ("RAM", "PC Parts"),
        ("Storage", "PC Parts"),
        ("Power Supplies", "PC Parts"),

        ("Games & Accessories", None),
        ("Games", "Games & Accessories"),
        ("Accessories", "Games & Accessories"),

        ("Services", None),
        ("Consultation", "Services"),
        ("Prebuilt", "Services"),
        ("Repair / Upgrade", "Services"),
    ]

    def get_category(name):
        return Category.query.filter_by(category_name=name).first()

    for name, parent_name in categories:
        parent = get_category(parent_name) if parent_name else None

        existing = get_category(name)
        if existing:
            continue

        new_cat = Category(
            category_name=name,
            parent_category_id=parent.category_id if parent else None
        )

        db.session.add(new_cat)

    db.session.commit()
    print("Categories seeded successfully!")
