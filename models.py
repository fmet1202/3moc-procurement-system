from datetime import datetime, timezone
from flask_login import UserMixin
from extensions import db

class AdminUser(UserMixin, db.Model):
    __tablename__ = "admin_user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

class Sector(db.Model):
    __tablename__ = "sector"
    id = db.Column(db.Integer, primary_key=True)
    lot_number = db.Column(db.String(20), nullable=False)
    title_en = db.Column(db.String(150), nullable=False)
    title_am = db.Column(db.String(150), nullable=True)
    items_summary = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=False)
    sort_order = db.Column(db.Integer, default=0)

class ContactPerson(db.Model):
    __tablename__ = "contact_person"
    id = db.Column(db.Integer, primary_key=True)
    role_en = db.Column(db.String(100), nullable=False)
    role_am = db.Column(db.String(100), nullable=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(50), nullable=False)
    sort_order = db.Column(db.Integer, default=0)

class Submission(db.Model):
    __tablename__ = "submission"
    id = db.Column(db.Integer, primary_key=True)
    organization = db.Column(db.String(150), nullable=False)
    contact_name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    tender_ref = db.Column(db.String(100), nullable=True)
    selected_lots = db.Column(db.String(255), nullable=True)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default="New")
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

class TenderSheet(db.Model):
    __tablename__ = "tender_sheet"
    id = db.Column(db.Integer, primary_key=True)
    tender_title = db.Column(db.String(200), nullable=False)
    client_name = db.Column(db.String(150), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    raw_data_json = db.Column(db.Text, nullable=True)