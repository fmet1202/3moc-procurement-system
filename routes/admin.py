from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from extensions import db, limiter
from models import AdminUser, Sector, ContactPerson, Submission

admin_bp = Blueprint("admin", __name__)

# --- AUTHENTICATION ---
@admin_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("10 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for("admin.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = AdminUser.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for("admin.dashboard"))
        flash("Invalid credentials.", "error")

    return render_template("admin/login.html")


@admin_bp.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("admin.login"))


@admin_bp.route("/change-password", methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == "POST":
        current_password = request.form.get("current_password", "")
        new_password = request.form.get("new_password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not check_password_hash(current_user.password_hash, current_password):
            flash("Current password is incorrect.", "error")
            return redirect(url_for("admin.change_password"))

        if len(new_password) < 10:
            flash("New password must be at least 10 characters.", "error")
            return redirect(url_for("admin.change_password"))

        if new_password != confirm_password:
            flash("New password and confirmation do not match.", "error")
            return redirect(url_for("admin.change_password"))

        if check_password_hash(current_user.password_hash, new_password):
            flash("New password must be different from the current password.", "error")
            return redirect(url_for("admin.change_password"))

        current_user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        flash("Password updated successfully.", "success")
        return redirect(url_for("admin.dashboard"))

    return render_template("admin/change_password.html")


# --- DASHBOARD ---
@admin_bp.route("/")
@login_required
def dashboard():
    return render_template(
        "admin/dashboard.html",
        sector_count=Sector.query.count(),
        submission_count=Submission.query.count(),
        new_submissions=Submission.query.filter_by(status="New").count(),
        recent_submissions=Submission.query.order_by(Submission.created_at.desc()).limit(6).all()
    )


# --- TENDER BID & SUPPLIER MATRIX ---
@admin_bp.route("/calculator")
@login_required
def calculator():
    return render_template("admin/calculator.html")


# --- SECTORS / LOTS CRUD ---
@admin_bp.route("/sectors")
@login_required
def sectors_list():
    sectors = Sector.query.order_by(Sector.sort_order).all()
    return render_template("admin/sectors.html", sectors=sectors)


@admin_bp.route("/sectors/new", methods=["GET", "POST"])
@login_required
def sector_new():
    if request.method == "POST":
        s = Sector(
            lot_number=request.form.get("lot_number", "").strip(),
            title_en=request.form.get("title_en", "").strip(),
            title_am=request.form.get("title_am", "").strip(),
            items_summary=request.form.get("items_summary", "").strip(),
            description=request.form.get("description", "").strip(),
            sort_order=int(request.form.get("sort_order") or 0)
        )
        db.session.add(s)
        db.session.commit()
        flash("New procurement sector created.", "success")
        return redirect(url_for("admin.sectors_list"))
    return render_template("admin/sector_form.html", sector=None)


@admin_bp.route("/sectors/<int:sector_id>/edit", methods=["GET", "POST"])
@login_required
def sector_edit(sector_id):
    sector = db.session.get(Sector, sector_id)
    if not sector:
        flash("Sector not found.", "error")
        return redirect(url_for("admin.sectors_list"))

    if request.method == "POST":
        sector.lot_number = request.form.get("lot_number", "").strip()
        sector.title_en = request.form.get("title_en", "").strip()
        sector.title_am = request.form.get("title_am", "").strip()
        sector.items_summary = request.form.get("items_summary", "").strip()
        sector.description = request.form.get("description", "").strip()
        sector.sort_order = int(request.form.get("sort_order") or 0)
        db.session.commit()
        flash("Sector updated successfully.", "success")
        return redirect(url_for("admin.sectors_list"))

    return render_template("admin/sector_form.html", sector=sector)


@admin_bp.route("/sectors/<int:sector_id>/delete", methods=["POST"])
@login_required
def sector_delete(sector_id):
    sector = db.session.get(Sector, sector_id)
    if sector:
        db.session.delete(sector)
        db.session.commit()
        flash("Sector removed.", "success")
    return redirect(url_for("admin.sectors_list"))


# --- PARTNER CONTACTS CRUD ---
@admin_bp.route("/contacts")
@login_required
def contacts_list():
    contacts = ContactPerson.query.order_by(ContactPerson.sort_order).all()
    return render_template("admin/contacts.html", contacts=contacts)


@admin_bp.route("/contacts/<int:contact_id>/edit", methods=["GET", "POST"])
@login_required
def contact_edit(contact_id):
    contact = db.session.get(ContactPerson, contact_id)
    if not contact:
        flash("Contact not found.", "error")
        return redirect(url_for("admin.contacts_list"))

    if request.method == "POST":
        contact.name = request.form.get("name", "").strip()
        contact.role_en = request.form.get("role_en", "").strip()
        contact.role_am = request.form.get("role_am", "").strip()
        contact.email = request.form.get("email", "").strip()
        contact.phone = request.form.get("phone", "").strip()
        db.session.commit()
        flash("Partner contact updated.", "success")
        return redirect(url_for("admin.contacts_list"))

    return render_template("admin/contact_form.html", contact=contact)


# --- INBOUND SUBMISSIONS ---
@admin_bp.route("/submissions")
@login_required
def submissions_list():
    submissions = Submission.query.order_by(Submission.created_at.desc()).all()
    return render_template("admin/submissions.html", submissions=submissions)


@admin_bp.route("/submissions/<int:sub_id>")
@login_required
def submission_detail(sub_id):
    sub = db.session.get(Submission, sub_id)
    if not sub:
        flash("Submission not found.", "error")
        return redirect(url_for("admin.submissions_list"))
    return render_template("admin/submission_detail.html", sub=sub)


@admin_bp.route("/submissions/<int:sub_id>/status", methods=["POST"])
@login_required
def submission_update_status(sub_id):
    sub = db.session.get(Submission, sub_id)
    if sub:
        sub.status = request.form.get("status", "New")
        db.session.commit()
        flash("Submission status updated.", "success")
    return redirect(url_for("admin.submission_detail", sub_id=sub_id))


@admin_bp.route("/submissions/<int:sub_id>/delete", methods=["POST"])
@login_required
def submission_delete(sub_id):
    sub = db.session.get(Submission, sub_id)
    if sub:
        db.session.delete(sub)
        db.session.commit()
        flash("Submission deleted.", "success")
    return redirect(url_for("admin.submissions_list"))