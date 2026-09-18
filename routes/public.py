import os
import threading
from types import SimpleNamespace
from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory
from extensions import db
from models import Sector, ContactPerson, Submission
from telegram_alert import send_telegram_rfq_alert

public_bp = Blueprint("public", __name__)

@public_bp.route("/")
def index():
    sectors = Sector.query.order_by(Sector.sort_order).limit(6).all()
    return render_template("index.html", sectors=sectors)

@public_bp.route("/about")
def about():
    contacts = ContactPerson.query.order_by(ContactPerson.sort_order).all()
    return render_template("about.html", contacts=contacts)

@public_bp.route("/sectors")
def sectors():
    all_sectors = Sector.query.order_by(Sector.sort_order).all()
    return render_template("sectors.html", sectors=all_sectors)

@public_bp.route("/rfq", methods=["GET", "POST"])
def rfq():
    if request.method == "POST":
        org = request.form.get("organization", "").strip()
        name = request.form.get("contact_name", "").strip()
        phone = request.form.get("phone", "").strip()
        email = request.form.get("email", "").strip()
        tender_ref = request.form.get("tender_ref", "").strip()
        message = request.form.get("message", "").strip()
        selected_lots = request.form.getlist("selected_lots")

        if not org or not name or not phone or not message:
            flash("Please fill in all required fields (Organization, Name, Phone, and Details).", "error")
            return redirect(url_for("public.rfq"))

        sub = Submission(
            organization=org,
            contact_name=name,
            phone=phone,
            email=email,
            tender_ref=tender_ref,
            selected_lots=", ".join(selected_lots) if selected_lots else "General Tender Lot",
            message=message,
            status="New"
        )
        db.session.add(sub)
        db.session.commit()

        # Snapshot the fields into a plain object BEFORE starting the thread.
        # After db.session.commit(), SQLAlchemy expires `sub`'s attributes so
        # the next read re-fetches from the DB — but that refetch needs an
        # active Flask app context, which the background thread doesn't have.
        # Reading the values here (still inside the request context) avoids
        # any DB/app-context access from inside the thread.
        alert_data = SimpleNamespace(
            organization=sub.organization,
            contact_name=sub.contact_name,
            phone=sub.phone,
            email=sub.email,
            tender_ref=sub.tender_ref,
            selected_lots=sub.selected_lots,
            message=sub.message,
        )

        # Send Telegram notification without blocking the response — a slow
        # or unreachable Telegram API should never delay the RFQ confirmation.
        threading.Thread(target=send_telegram_rfq_alert, args=(alert_data,), daemon=True).start()

        flash("Your proforma request has been recorded. Our team will review your specifications.", "success")
        return redirect(url_for("public.rfq"))

    sectors = Sector.query.order_by(Sector.sort_order).all()
    return render_template("rfq.html", sectors=sectors)

@public_bp.route("/profile")
def profile():
    sectors = Sector.query.order_by(Sector.sort_order).all()
    contacts = ContactPerson.query.order_by(ContactPerson.sort_order).all()
    return render_template("profile.html", sectors=sectors, contacts=contacts)

@public_bp.route("/contact")
def contact():
    contacts = ContactPerson.query.order_by(ContactPerson.sort_order).all()
    return render_template("contact.html", contacts=contacts)

# --- PWA ROUTES ---
@public_bp.route("/sw.js")
def service_worker():
    response = send_from_directory(os.path.join(public_bp.root_path, "../static/js"), "sw.js")
    response.headers["Content-Type"] = "application/javascript"
    response.headers["Service-Worker-Allowed"] = "/"
    return response

@public_bp.route("/manifest.json")
def manifest():
    response = send_from_directory(os.path.join(public_bp.root_path, "../static"), "manifest.json")
    response.headers["Content-Type"] = "application/manifest+json"
    return response