"""
One-step seed script to initialize admin and authentic Ethiopian government lots.
Run with: python seed.py
"""
import os
import secrets
from werkzeug.security import generate_password_hash
from app import create_app
from extensions import db
from models import AdminUser, Sector, ContactPerson

app = create_app()

DEFAULT_SECTORS = [
    (
        "LOT 01",
        "Office Stationery & Paper Consumables",
        "የቢሮ መፃፊያና ወረቀት ቁሳቁሶች",
        "A4 Photocopy Paper, Envelopes, Box Files, Ballpoint Pens, Toners, Fasteners",
        "Bulk supply of premium duplicating papers, official writing ledgers, toners, filing accessories, and standard office desk consumables.",
        1
    ),
    (
        "LOT 02",
        "Sanitary, Cleaning & Washroom Chemicals",
        "የፅዳትና ንፅህና መጠበቂያ ቁሳቁሶች",
        "Jumbo Toilet Rolls, Floor Detergents, Bleach, Handwash, Brooms & Mops",
        "Industrial and institutional hygiene solutions including multi-surface disinfectants, hand sanitizers, jumbo rolls, soaps, and custodial cleaning tools.",
        2
    ),
    (
        "LOT 03",
        "Kitchen Utensils & Meeting Catering Wares",
        "የወጥ ቤትና የምግብ ማቅረቢያ እቃዎች",
        "Stainless Steel Thermos, Tea Urns, Glassware, Porcelain Cups, Cutlery, Trays",
        "Complete institutional catering essentials for ministry cafeterias, executive boardrooms, meeting hospitality, and central breakrooms.",
        3
    ),
    (
        "LOT 04",
        "Office Furniture & Storage Fixtures",
        "የቢሮ ፈርኒቸርና ሰነድ ማስቀመጫ",
        "High-Back Swivel Chairs, Executive Desks, 4-Drawer Steel Cabinets, Meeting Tables",
        "Durable, ergonomic office fittings, modular workstations, safe document filing lockers, and boardroom conference furniture.",
        4
    ),
    (
        "LOT 05",
        "IT Hardware, Peripherals & Electronics",
        "የኮምፒውተርና የኤሌክትሮኒክስ እቃዎች",
        "Heavy-Duty Multi-function Printers, Desktop Computers, UPS, Cat6 Cables, Adapters",
        "Procurement of institutional electronics, uninterrupted power backups (UPS), network cables, monitors, and essential computer consumables.",
        5
    ),
    (
        "LOT 06",
        "Staff Uniforms & Protective Workwear (PPE)",
        "የደንብ ልብስና የደህንነት መጠበቂያ አልባሳት",
        "Dust Coats, Security Attire, Safety Boots, Heavy-Duty Overalls, High-Vis Vests",
        "Custom-tailored institutional apparel, security guards uniforms, janitorial dust coats, and labor-compliance safety gear.",
        6
    ),
    (
        "LOT 07",
        "Printing, Publishing & Institutional Ledger Works",
        "የህትመትና ልዩ ልዩ የጨረታ እቃዎች",
        "Custom Receipt Pads, Payment Vouchers, Rubber Stamps, Letterheads, Banners",
        "Authorized government stationery printing including sequential payment vouchers, custom stamps, official ledgers, and institutional materials.",
        7
    ),
]

DEFAULT_CONTACTS = [
    ("Managing Partner — Procurement & Sourcing", "የግዥና አቅርቦት ኃላፊ", "Abrham Sleshi", "abrhamisyoum01@gmail.com", "+251 97 373 7398", 1),
    ("Partner — Tender Bids & Compliance", "የጨረታና ህግ ተገዢነት ኃላፊ", "Partner 2", "compliance@3moc.et", "+251 91 100 0001", 2),
    ("Partner — Client Relations & Logistics", "የደንበኞች ግንኙነትና ስርጭት", "Partner 3", "logistics@3moc.et", "+251 91 100 0002", 3),
]

with app.app_context():
    os.makedirs("instance", exist_ok=True)
    db.create_all()

    if not AdminUser.query.filter_by(username="admin").first():
        initial_password = os.environ.get("ADMIN_INITIAL_PASSWORD") or secrets.token_urlsafe(12)
        db.session.add(AdminUser(
            username="admin",
            password_hash=generate_password_hash(initial_password)
        ))
        print("=" * 60)
        print("[+] Admin user created -> Username: admin")
        print(f"[+] One-time initial password: {initial_password}")
        print("    Log in and use 'Change Password' immediately.")
        print("=" * 60)

    if Sector.query.count() == 0:
        for lot, en, am, items, desc, order in DEFAULT_SECTORS:
            db.session.add(Sector(
                lot_number=lot, title_en=en, title_am=am,
                items_summary=items, description=desc, sort_order=order
            ))
        print(f"[+] Loaded {len(DEFAULT_SECTORS)} procurement lots.")

    if ContactPerson.query.count() == 0:
        for role_en, role_am, name, email, phone, order in DEFAULT_CONTACTS:
            db.session.add(ContactPerson(
                role_en=role_en, role_am=role_am, name=name,
                email=email, phone=phone, sort_order=order
            ))
        print(f"[+] Loaded {len(DEFAULT_CONTACTS)} partner profiles.")

    db.session.commit()
    print("[✓] Seed completed successfully.")