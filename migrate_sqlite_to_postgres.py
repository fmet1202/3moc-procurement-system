"""
One-off migration: copies existing data out of local SQLite (instance/3moc.db)
into whatever DATABASE_URL points at (Render managed Postgres).

Usage:
    export DATABASE_URL="postgresql://user:pass@host:port/dbname"
    export SECRET_KEY="temp-for-migration"
    python migrate_sqlite_to_postgres.py
"""
import os
import sqlite3

from app import create_app
from extensions import db
from models import AdminUser, Sector, ContactPerson, Submission, TenderSheet

SQLITE_PATH = os.path.join(os.path.dirname(__file__), "instance", "3moc.db")

def fetch_all(table):
    conn = sqlite3.connect(SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute(f"SELECT * FROM {table}").fetchall()
    conn.close()
    return [dict(r) for r in rows]

def migrate():
    if not os.path.exists(SQLITE_PATH):
        print(f"No SQLite database found at {SQLITE_PATH} — nothing to migrate.")
        return

    app = create_app()
    with app.app_context():
        moved = {"admin_user": 0, "sector": 0, "contact_person": 0, "submission": 0, "tender_sheet": 0}

        for row in fetch_all("admin_user"):
            if not db.session.get(AdminUser, row["id"]):
                db.session.add(AdminUser(**row))
                moved["admin_user"] += 1

        for row in fetch_all("sector"):
            if not db.session.get(Sector, row["id"]):
                db.session.add(Sector(**row))
                moved["sector"] += 1

        for row in fetch_all("contact_person"):
            if not db.session.get(ContactPerson, row["id"]):
                db.session.add(ContactPerson(**row))
                moved["contact_person"] += 1

        for row in fetch_all("submission"):
            if not db.session.get(Submission, row["id"]):
                db.session.add(Submission(**row))
                moved["submission"] += 1

        try:
            for row in fetch_all("tender_sheet"):
                if not db.session.get(TenderSheet, row["id"]):
                    db.session.add(TenderSheet(**row))
                    moved["tender_sheet"] += 1
        except sqlite3.OperationalError:
            pass

        db.session.commit()
        print("Migration complete:")
        for table, count in moved.items():
            print(f"  {table}: {count} row(s) copied")

if __name__ == "__main__":
    migrate()